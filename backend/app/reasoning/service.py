from __future__ import annotations

from typing import Any
from sqlalchemy.orm import Session

from app.environmental_data.service import collect_environmental_data
from app.reasoning.reasoning_engine import execute_environmental_reasoning
from app.reasoning.schemas import ReasoningRequest, ReasoningResponse


def analyze_environment(
    db: Session,
    request: ReasoningRequest,
) -> ReasoningResponse:
    # 1. Collect live environmental data for requested coordinates
    env_data = collect_environmental_data(
        latitude=request.latitude,
        longitude=request.longitude,
        radius_km=request.radius_km or 10.0,
        db=db,
    )

    profile = env_data.get("profile", {})
    provider_status = env_data.get("provider_status", {})

    # 2. Run multi-metric reasoning engine
    return execute_environmental_reasoning(
        db=db,
        latitude=request.latitude,
        longitude=request.longitude,
        profile=profile,
        provider_status=provider_status,
        user_context=request.context,
        text_context=request.text_context,
    )


def run_environmental_reasoning(
    db: Session,
    request: ReasoningRequest,
) -> ReasoningResponse:
    return analyze_environment(db=db, request=request)
