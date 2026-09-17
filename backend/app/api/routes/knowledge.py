from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.knowledge.embedding import EmbeddingConfigurationError
from app.knowledge.retrieval import retrieve
from app.knowledge.schemas import KnowledgeSearchRequest, KnowledgeSearchResponse, KnowledgeSearchResult, KnowledgeSource
from app.models import Document, DocumentChunk

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.get("/sources", response_model=list[KnowledgeSource])
def list_sources(db: Session = Depends(get_db)):
    try:
        statement = select(Document, func.count(DocumentChunk.id)).outerjoin(DocumentChunk).group_by(Document.id).order_by(Document.created_at.desc())
        return [KnowledgeSource(id=document.id, title=document.title, organization=document.organization, year=document.year, source_type=document.source_type, source_url=document.source_url, topic=document.topic, environmental_metrics=document.environmental_metrics or [], ingestion_status=document.ingestion_status, chunk_count=count) for document, count in db.execute(statement)]
    except SQLAlchemyError as error:
        raise HTTPException(status_code=503, detail="Knowledge sources are unavailable.") from error


@router.post("/search", response_model=KnowledgeSearchResponse)
def search_knowledge(payload: KnowledgeSearchRequest, db: Session = Depends(get_db)):
    try:
        rows = retrieve(db, payload.query, payload.top_k, payload.metrics)
        results = [KnowledgeSearchResult(document_id=document.id, title=document.title, organization=document.organization, year=document.year, source_type=document.source_type, source_url=document.source_url, chunk_id=chunk.id, text=chunk.content, relevance_score=round(score, 6), matched_metrics=matched) for score, document, chunk, matched in rows]
        return KnowledgeSearchResponse(query=payload.query, results=results)
    except EmbeddingConfigurationError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except SQLAlchemyError as error:
        raise HTTPException(status_code=503, detail="Knowledge search is unavailable.") from error
