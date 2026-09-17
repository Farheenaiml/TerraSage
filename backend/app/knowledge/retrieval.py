import math

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.knowledge.embedding import EmbeddingProvider
from app.models import Document, DocumentChunk


def cosine_similarity(left: list[float], right: list[float]) -> float:
    denominator = math.sqrt(sum(value * value for value in left)) * math.sqrt(sum(value * value for value in right))
    return sum(a * b for a, b in zip(left, right)) / denominator if denominator else 0.0


def retrieve(db: Session, query: str, top_k: int, metrics: list[str]):
    query_vector = EmbeddingProvider().embed([query])[0]
    rows = db.execute(select(Document, DocumentChunk).join(DocumentChunk, DocumentChunk.document_id == Document.id).where(Document.ingestion_status == "INGESTED").order_by(DocumentChunk.embedding.cosine_distance(query_vector)).limit(top_k)).all()
    results = []
    query_text = query.lower()
    for document, chunk in rows:
        if not chunk.embedding:
            continue
        score = cosine_similarity(query_vector, list(chunk.embedding))
        chunk_metrics = set((chunk.metadata_json or {}).get("metrics", []))
        matched = sorted(chunk_metrics.intersection(metrics)) if metrics else sorted(metric for metric in chunk_metrics if metric.replace("_", " ") in query_text or metric in query_text)
        results.append((score, document, chunk, matched))
    return results
