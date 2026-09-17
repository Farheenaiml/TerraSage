from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy import select, update

from app.models.recommendation import RecommendationRecord
from app.reasoning.schemas import ReasoningRequest, ReasoningResponse, LinkedEvidence
from app.reasoning.service import analyze_environment
from app.recommendations.schemas import (
    RecommendationDto,
    RecommendationGenerateRequest,
    RecommendationListResponse,
)
from app.recommendations.recommendation_engine import generate_recommendations_from_reasoning


def _record_to_dto(rec: RecommendationRecord) -> RecommendationDto:
    ev_list = []
    if isinstance(rec.evidence, list):
        for e in rec.evidence:
            if isinstance(e, dict):
                ev_list.append(LinkedEvidence(**e))
            elif isinstance(e, LinkedEvidence):
                ev_list.append(e)

    return RecommendationDto(
        id=rec.id,
        title=rec.title,
        description=rec.description,
        rationale=rec.rationale,
        impacted_metrics=rec.impacted_metrics or [],
        expected_impact=rec.expected_impact,
        time_horizon=rec.time_horizon,
        confidence=rec.confidence,
        confidence_score=rec.confidence_score,
        confidence_rationale=rec.confidence_rationale,
        priority=rec.priority,
        category=rec.category,
        evidence=ev_list,
        status=rec.status,
        limitations=rec.limitations or [],
        relationship_id=rec.relationship_id,
        created_at=rec.created_at.isoformat() if rec.created_at else None,
    )


def generate_recommendations(
    req: RecommendationGenerateRequest,
    db: Session,
) -> RecommendationListResponse:
    """Generates recommendations from existing reasoning or runs reasoning on demand."""
    reasoning_res: ReasoningResponse

    if req.reasoning_response:
        reasoning_res = req.reasoning_response
    else:
        if req.latitude is None or req.longitude is None:
            raise ValueError("Latitude and longitude are required when reasoning_response is not provided.")
        
        reasoning_req = ReasoningRequest(
            latitude=req.latitude,
            longitude=req.longitude,
            radius_km=req.radius_km or 10.0,
            context=req.context,
            text_context=req.text_context,
        )
        reasoning_res = analyze_environment(db=db, request=reasoning_req)

    dtos = generate_recommendations_from_reasoning(reasoning_res)

    # Persist in database
    loc = reasoning_res.location or {}
    lat = loc.get("latitude")
    lon = loc.get("longitude")
    loc_id = f"coord:{lat:.6f}:{lon:.6f}" if lat is not None and lon is not None else None

    # Clear prior suggestions for this exact coordinate to avoid stale duplicates
    if loc_id:
        existing = db.execute(
            select(RecommendationRecord).where(
                RecommendationRecord.location_id == loc_id,
                RecommendationRecord.status == "suggested",
            )
        ).scalars().all()
        for old in existing:
            db.delete(old)
        db.flush()

    for dto in dtos:
        record = RecommendationRecord(
            id=dto.id,
            location_id=loc_id,
            latitude=lat,
            longitude=lon,
            title=dto.title,
            description=dto.description,
            rationale=dto.rationale,
            impacted_metrics=dto.impacted_metrics,
            expected_impact=dto.expected_impact,
            time_horizon=dto.time_horizon,
            confidence=dto.confidence,
            confidence_score=dto.confidence_score,
            confidence_rationale=dto.confidence_rationale,
            priority=dto.priority,
            category=dto.category,
            evidence=[e.model_dump(by_alias=True) for e in dto.evidence],
            status=dto.status,
            limitations=dto.limitations,
            relationship_id=dto.relationship_id,
        )
        db.add(record)

    db.commit()

    return RecommendationListResponse(items=dtos, total=len(dtos))


def list_recommendations(
    db: Session,
    status: str | None = None,
) -> RecommendationListResponse:
    stmt = select(RecommendationRecord).order_by(RecommendationRecord.created_at.desc())
    if status and status.lower() != "all":
        stmt = stmt.where(RecommendationRecord.status == status.lower())

    records = db.execute(stmt).scalars().all()
    dtos = [_record_to_dto(r) for r in records]
    return RecommendationListResponse(items=dtos, total=len(dtos))


def get_recommendation(
    rec_id: str,
    db: Session,
) -> RecommendationDto | None:
    rec = db.execute(
        select(RecommendationRecord).where(RecommendationRecord.id == rec_id)
    ).scalar_one_or_none()
    if not rec:
        return None
    return _record_to_dto(rec)


def update_recommendation_status(
    rec_id: str,
    status: str,
    db: Session,
) -> RecommendationDto:
    valid_statuses = {"suggested", "in-progress", "implemented", "dismissed"}
    if status.lower() not in valid_statuses:
        raise ValueError(f"Invalid status '{status}'. Must be one of {valid_statuses}")

    rec = db.execute(
        select(RecommendationRecord).where(RecommendationRecord.id == rec_id)
    ).scalar_one_or_none()
    if not rec:
        raise ValueError(f"Recommendation with id '{rec_id}' not found.")

    rec.status = status.lower()
    db.commit()
    db.refresh(rec)
    return _record_to_dto(rec)
