from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.recommendations.schemas import (
    RecommendationDto,
    RecommendationGenerateRequest,
    RecommendationListResponse,
    RecommendationStatusUpdateRequest,
)
from app.recommendations import service as rec_service

router = APIRouter(prefix="", tags=["recommendations"])


@router.post(
    "/generate",
    response_model=RecommendationListResponse,
    summary="Generate evidence-backed recommendations directly from multi-metric reasoning",
)
def generate_recommendations(
    request: RecommendationGenerateRequest,
    db: Session = Depends(get_db),
) -> RecommendationListResponse:
    try:
        return rec_service.generate_recommendations(request, db=db)
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {err}",
        )


@router.get(
    "",
    response_model=list[RecommendationDto],
    summary="List all recommendations with optional status filter",
)
def list_recommendations(
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
) -> list[RecommendationDto]:
    return rec_service.list_recommendations(db=db, status=status_filter).items


@router.get(
    "/{recommendation_id}",
    response_model=RecommendationDto,
    summary="Get single recommendation by ID",
)
def get_recommendation(
    recommendation_id: str,
    db: Session = Depends(get_db),
) -> RecommendationDto:
    rec = rec_service.get_recommendation(recommendation_id, db=db)
    if not rec:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Recommendation '{recommendation_id}' not found.",
        )
    return rec


@router.patch(
    "/{recommendation_id}/status",
    response_model=RecommendationDto,
    summary="Update recommendation status lifecycle",
)
def update_recommendation_status(
    recommendation_id: str,
    payload: RecommendationStatusUpdateRequest,
    db: Session = Depends(get_db),
) -> RecommendationDto:
    try:
        return rec_service.update_recommendation_status(
            recommendation_id, status=payload.status, db=db
        )
    except ValueError as err:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
