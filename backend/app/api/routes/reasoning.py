from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.reasoning.schemas import ReasoningRequest, ReasoningResponse
from app.reasoning.service import analyze_environment

router = APIRouter(prefix="/api/reasoning", tags=["reasoning"])


@router.post("/analyze", response_model=ReasoningResponse)
def analyze(payload: ReasoningRequest, db: Session = Depends(get_db)) -> ReasoningResponse:
    try:
        return analyze_environment(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Environmental reasoning failed: {exc}") from exc
