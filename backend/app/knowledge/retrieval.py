import math
import logging
from sqlalchemy import select, or_
from sqlalchemy.orm import Session

from app.core.config import settings
from app.knowledge.embedding import EmbeddingProvider, EmbeddingConfigurationError
from app.models import Document, DocumentChunk

logger = logging.getLogger(__name__)


def cosine_similarity(left: list[float], right: list[float]) -> float:
    denominator = math.sqrt(sum(value * value for value in left)) * math.sqrt(sum(value * value for value in right))
    return sum(a * b for a, b in zip(left, right)) / denominator if denominator else 0.0


def retrieve(db: Session, query: str, top_k: int = 10, metrics: list[str] = None):
    metrics = metrics or []
    query_text = (query or "").strip().lower()
    
    # 1. Attempt Vector Semantic Retrieval
    try:
        query_vector = EmbeddingProvider().embed([query])[0]
        rows = db.execute(
            select(Document, DocumentChunk)
            .join(DocumentChunk, DocumentChunk.document_id == Document.id)
            .where(Document.ingestion_status == "INGESTED")
            .order_by(DocumentChunk.embedding.cosine_distance(query_vector))
            .limit(top_k)
        ).all()
        
        results = []
        for document, chunk in rows:
            if not chunk.embedding:
                continue
            score = cosine_similarity(query_vector, list(chunk.embedding))
            chunk_metrics = set((chunk.metadata_json or {}).get("metrics", []))
            matched = (
                sorted(chunk_metrics.intersection(metrics))
                if metrics
                else sorted(metric for metric in chunk_metrics if metric.replace("_", " ") in query_text or metric in query_text)
            )
            results.append((score, document, chunk, matched))
        if results:
            return results
    except Exception as exc:
        logger.warning(f"Vector search failed, falling back to lexical search: {exc}")

    # 2. Resilient Fallback: Lexical / Keyword Search across Chunks & Documents
    pattern = f"%{query_text}%"
    rows = db.execute(
        select(Document, DocumentChunk)
        .join(DocumentChunk, DocumentChunk.document_id == Document.id)
        .where(
            Document.ingestion_status == "INGESTED",
            or_(
                DocumentChunk.content.ilike(pattern),
                Document.title.ilike(pattern),
                Document.topic.ilike(pattern),
                Document.organization.ilike(pattern)
            )
        )
        .limit(top_k)
    ).all()

    results = []
    for document, chunk in rows:
        chunk_metrics = set((chunk.metadata_json or {}).get("metrics", []))
        matched = (
            sorted(chunk_metrics.intersection(metrics))
            if metrics
            else sorted(metric for metric in chunk_metrics if metric.replace("_", " ") in query_text or metric in query_text)
        )
        # Compute relevance score based on occurrence frequency
        content_lower = (chunk.content or "").lower()
        title_lower = (document.title or "").lower()
        count = content_lower.count(query_text) + (title_lower.count(query_text) * 3)
        score = min(0.95, 0.65 + (count * 0.05))
        results.append((score, document, chunk, matched))

    # Sort descending by relevance score
    results.sort(key=lambda x: x[0], reverse=True)
    return results
