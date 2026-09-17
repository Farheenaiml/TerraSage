from __future__ import annotations

from typing import Any
from pydantic import Field, model_validator

from app.reasoning.schemas import ApiModel, LinkedEvidence
from app.recommendations.schemas import RecommendationDto


class ConversationMessageRequest(ApiModel):
    conversation_id: str | None = None
    message: str | None = None
    content: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    radius_km: float | None = Field(default=10.0, ge=0.1, le=1000)
    structured_context: dict[str, Any] | None = None
    land_use: str | None = None

    @model_validator(mode="before")
    @classmethod
    def unify_message_content(cls, data: Any) -> Any:
        if isinstance(data, dict):
            msg = data.get("message") or data.get("content")
            if msg:
                data["message"] = msg
                data["content"] = msg
        return data


class EnvironmentalContextDto(ApiModel):
    known: list[dict[str, Any]] = []
    missing: list[dict[str, Any]] = []
    location_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    land_use: str | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)
    soilgrids_available: bool = False
    data_sources: list[str] = Field(default_factory=list)


class ConversationMessageResponse(ApiModel):
    conversation_id: str
    response: str
    message: str | None = None
    response_type: str  # "clarification" | "environmental_analysis" | "explanation" | "pipeline_direct" | "analysis" | "recommendation" | "evidence"
    clarification_required: bool = False
    clarification_needed: bool = False
    clarification_question: str | None = None
    environmental_context: EnvironmentalContextDto = Field(default_factory=EnvironmentalContextDto)
    reasoning_summary: str | None = None
    recommendations: list[RecommendationDto] = []
    evidence: list[LinkedEvidence] = []
    limitations: list[str] = []
    llm_used: str | None = None
    llm_available: bool = True

    @model_validator(mode="before")
    @classmethod
    def sync_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            if "response" in data and not data.get("message"):
                data["message"] = data["response"]
            elif "message" in data and not data.get("response"):
                data["response"] = data["message"]
            if "clarification_required" in data and "clarification_needed" not in data:
                data["clarification_needed"] = data["clarification_required"]
            elif "clarification_needed" in data and "clarification_required" not in data:
                data["clarification_required"] = data["clarification_needed"]
        return data


class ConversationMessageItem(ApiModel):
    id: str
    role: str  # "user" | "assistant"
    content: str
    response_type: str | None = None
    clarification_question: str | None = None
    evidence_refs: list[str] = []
    timestamp: str


class ConversationDto(ApiModel):
    id: str
    title: str
    messages: list[ConversationMessageItem] = []
    environmental_context: EnvironmentalContextDto = Field(default_factory=EnvironmentalContextDto)
    created_at: str
    updated_at: str
    message_count: int = 0


class ConversationCreateRequest(ApiModel):
    title: str = "New Conversation"
    location_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    user_context: dict[str, Any] | None = None
