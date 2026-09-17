from __future__ import annotations

from typing import Any
from pydantic import BaseModel, ConfigDict, Field


class ApiModel(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        alias_generator=lambda value: ''.join(
            [value.split('_')[0], *[part.capitalize() for part in value.split('_')[1:]]]
        ),
    )


class ReasoningRequest(ApiModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float | None = Field(default=10.0, ge=0.1, le=1000)
    context: dict[str, Any] | None = None
    text_context: str | None = None


class MetricContext(ApiModel):
    metric: str
    value: float | int | str | None = None
    unit: str | None = None
    period: str | None = None
    source: str | None = None
    availability: str = "AVAILABLE"  # AVAILABLE, UNAVAILABLE, UNKNOWN, NOT_APPLICABLE
    unavailability_reason: str | None = None
    metadata: dict[str, Any] = {}


class LinkedEvidence(ApiModel):
    document_id: str
    chunk_id: str
    source: str
    title: str
    organization: str
    publication_year: int | None = None
    excerpt: str
    retrieval_score: float
    source_url: str | None = None
    matched_metrics: list[str] = []


class EnvironmentalRelationship(ApiModel):
    relationship_id: str
    relationship_type: str
    title: str
    metrics: list[str]
    metrics_count: int
    is_multi_metric: bool  # True if >= 3 metrics
    fallback_label: str | None = None  # e.g. "Limited 2-metric analysis" if < 3
    interpretation: str
    evidence_status: str  # "supported" or "insufficient_evidence"
    evidence: list[LinkedEvidence] = []
    limitations: list[str] = []


class ReasoningResponse(ApiModel):
    location: dict[str, Any]
    user_context: dict[str, Any] = {}
    available_metrics: list[MetricContext]
    unavailable_metrics: list[MetricContext]
    relationships: list[EnvironmentalRelationship]
    overall_interpretation: str
    limitations: list[str]
