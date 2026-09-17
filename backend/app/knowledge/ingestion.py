import hashlib
import re
from io import BytesIO
from html.parser import HTMLParser

import httpx
from httpx import HTTPStatusError
from pypdf import PdfReader
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.knowledge.embedding import EmbeddingProvider
from app.knowledge.sources import SourceDefinition
from app.models import Document, DocumentChunk, Embedding, EvidenceMetadata


class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self.skip = False

    def handle_starttag(self, tag, attrs):
        self.skip = tag in {"script", "style", "noscript"}

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript"}:
            self.skip = False

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def extract_text(response: httpx.Response) -> str:
    content_type = response.headers.get("content-type", "")
    if "pdf" in content_type or response.url.path.lower().endswith(".pdf"):
        return clean_text(" ".join(page.extract_text() or "" for page in PdfReader(BytesIO(response.content)).pages))
    parser = TextExtractor()
    parser.feed(response.text)
    return clean_text(" ".join(parser.parts))


def chunk_text(text: str, size: int = 1200, overlap: int = 150) -> list[str]:
    words = text.split()
    chunks = []
    step = max(1, size - overlap)
    for start in range(0, len(words), step):
        chunk = " ".join(words[start : start + size])
        if chunk:
            chunks.append(chunk)
        if start + size >= len(words):
            break
    return chunks


METRIC_TERMS = {
    "soil_ph": ("soil ph", "soil acidity", "soil alkalinity"),
    "soil_organic_carbon": ("soil organic carbon", "organic carbon", "soil carbon"),
    "soil_moisture": ("soil moisture", "water retention"),
    "land_use": ("land use", "land-use"),
    "land_cover": ("land cover", "land-cover", "vegetation cover"),
    "species_richness": ("species richness", "species diversity"),
    "biodiversity": ("biodiversity", "biological diversity"),
    "habitat_diversity": ("habitat diversity", "habitat heterogeneity"),
    "temperature": ("temperature", "warming"),
    "rainfall": ("rainfall", "precipitation"),
    "pollution": ("pollution", "contaminant", "contamination"),
    "deforestation": ("deforestation", "forest loss", "forest degradation"),
    "soil_biodiversity": ("soil biodiversity", "soil organisms", "soil biota"),
    "water_availability": ("water availability", "water scarcity", "water resource"),
    "vegetation": ("vegetation", "plant cover", "crop cover"),
    "agriculture": ("agriculture", "agricultural", "farming", "crop"),
    "agroforestry": ("agroforestry", "agro-forestry"),
    "intercropping": ("intercropping", "inter-cropping"),
    "cover_crops": ("cover crop", "cover-crops"),
    "monoculture": ("monoculture", "mono-crop", "single crop"),
    "land_degradation": ("land degradation", "degraded land", "land restoration"),
}


def tag_metrics(text: str) -> list[str]:
    normalized = text.lower()
    return [metric for metric, terms in METRIC_TERMS.items() if any(term in normalized for term in terms)]


def register_source(db: Session, source: SourceDefinition) -> Document:
    document = db.scalar(select(Document).where(Document.source_url == source.source_url))
    if document:
        return document
    document = Document(
        title=source.title,
        organization=source.organization,
        year=source.year,
        source_type=source.source_type,
        source_url=source.source_url,
        topic=source.topic,
        environmental_metrics=list(source.environmental_metrics),
        ingestion_status="REGISTERED",
    )
    db.add(document)
    db.commit()
    db.refresh(document)
    db.add(EvidenceMetadata(document_id=document.id, evidence_type=source.source_type, organization=source.organization, publication_year=source.year, metrics=list(source.environmental_metrics)))
    db.commit()
    return document


def ingest_source(db: Session, source: SourceDefinition) -> Document:
    document = register_source(db, source)
    if document.ingestion_status == "INGESTED":
        return document
    try:
        response = httpx.get(source.source_url, headers={"User-Agent": "TerraSage knowledge ingestion/1.0"}, follow_redirects=True, timeout=60)
        response.raise_for_status()
        text = extract_text(response)
        chunks = chunk_text(text)
        if not chunks:
            raise RuntimeError("No extractable text found")
        vectors = EmbeddingProvider().embed(chunks)
        existing = {chunk.chunk_index for chunk in db.scalars(select(DocumentChunk).where(DocumentChunk.document_id == document.id))}
        for index, (content, vector) in enumerate(zip(chunks, vectors)):
            if index in existing:
                continue
            chunk = DocumentChunk(document_id=document.id, content=content, chunk_index=index, metadata_json={"metrics": tag_metrics(content), "content_hash": hashlib.sha256(content.encode()).hexdigest()}, embedding=vector)
            db.add(chunk)
            db.flush()
            db.add(Embedding(chunk_id=chunk.id, model_name=EmbeddingProvider().model, vector=vector))
        document.ingestion_status = "INGESTED"
        document.ingestion_error = None
        db.commit()
    except HTTPStatusError as error:
        document.ingestion_status = "INGESTION_BLOCKED" if error.response.status_code == 403 else "FAILED"
        document.ingestion_error = f"HTTP {error.response.status_code}: {error.request.url}"
        db.commit()
        raise
    except Exception as error:
        document.ingestion_status = "FAILED"
        document.ingestion_error = str(error)[:1000]
        db.commit()
        raise
    return document
