from pydantic import BaseModel, Field, HttpUrl


class KnowledgeSearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=20)
    metrics: list[str] = Field(default_factory=list, max_length=20)


class KnowledgeSearchResult(BaseModel):
    document_id: str
    title: str
    organization: str
    year: int | None
    source_type: str
    source_url: HttpUrl
    chunk_id: str
    text: str
    relevance_score: float
    matched_metrics: list[str]


class KnowledgeSearchResponse(BaseModel):
    query: str
    results: list[KnowledgeSearchResult]


class KnowledgeSource(BaseModel):
    id: str
    title: str
    organization: str
    year: int | None
    source_type: str
    source_url: HttpUrl
    topic: str
    environmental_metrics: list[str]
    ingestion_status: str
    chunk_count: int
