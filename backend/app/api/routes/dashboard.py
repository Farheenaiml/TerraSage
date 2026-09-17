from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api.routes.environment import current_user_id, serialize_profile
from app.core.database import get_db
from app.schemas.environment import DashboardResponse
from app.services.dashboard_service import build_dashboard
from app.services.environment_service import get_profile
from app.models import Document

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
def read_dashboard(user_id: str = Depends(current_user_id), db: Session = Depends(get_db)):
    try:
        response = build_dashboard(serialize_profile(get_profile(db, user_id)))
        response.evidence_summary = {
            "total": db.scalar(select(func.count(Document.id)).where(Document.ingestion_status == "INGESTED")) or 0,
            "recentCount": 0,
            "byType": {},
        }
        return response
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Dashboard data is unavailable.") from exc