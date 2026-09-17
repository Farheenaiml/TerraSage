from __future__ import annotations

from typing import Any
from pydantic import Field

from app.reasoning.schemas import ApiModel, LinkedEvidence, ReasoningResponse


class RecommendationDto(ApiModel):
    id: str
    title: str
    description: str
    rationale: str
    impacted_metrics: list[str] = []
    expected_impact: str
    time_horizon: str  # "short-term" | "medium-term" | "long-term"
    confidence: str  # "high" | "medium" | "low"
    confidence_score: float | None = None  # None when not defensibly quantifiable; no fake percentages
    confidence_rationale: str
    priority: str  # "high" | "medium" | "low"
    category: str
    evidence: list[LinkedEvidence] = []
    status: str = "suggested"  # "suggested" | "in-progress" | "implemented" | "dismissed"
    limitations: list[str] = []
    relationship_id: str | None = None
    created_at: str | None = None


class RecommendationGenerateRequest(ApiModel):
    reasoning_response: ReasoningResponse | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    radius_km: float | None = Field(default=10.0, ge=0.1, le=1000)
    context: dict[str, Any] | None = None
    text_context: str | None = None


class RecommendationListResponse(ApiModel):
    items: list[RecommendationDto]
    total: int


class RecommendationStatusUpdateRequest(ApiModel):
    status: str
