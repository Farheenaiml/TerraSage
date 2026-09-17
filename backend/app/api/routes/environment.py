from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.environmental_data.service import build_environmental_profile, collect_environmental_data, validate_coordinates
from app.models.environment import EnvironmentalObservation
from app.schemas.environment import (
    EnvironmentalDataResponse,
    EnvironmentalLocationRequest,
    EnvironmentalProfilePayload,
    EnvironmentalProfileResponse,
)
from app.services.environment_service import field_status, get_profile, upsert_profile

router = APIRouter(prefix="/api/environment", tags=["environment"])


def current_user_id(x_user_id: str | None = Header(default=None)) -> str:
    return x_user_id or "00000000-0000-0000-0000-000000000001"


def serialize_profile(profile) -> EnvironmentalProfileResponse | None:
    if profile is None:
        return None
    available, missing = field_status(profile)
    return EnvironmentalProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        region=profile.region,
        latitude=profile.latitude,
        longitude=profile.longitude,
        soil=profile.soil,
        climate=profile.climate,
        land=profile.land,
        biodiversity=profile.biodiversity,
        human_impact=profile.human_impact,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
        available_fields=available,
        missing_fields=missing,
    )


def persist_observations(db: Session, latitude: float, longitude: float, observations: list[dict]) -> None:
    if not observations:
        return
    location_id = f"coord:{latitude:.6f}:{longitude:.6f}"
    records = []
    for item in observations:
        val = item.get("value")
        numeric_val = None
        if isinstance(val, (int, float)):
            numeric_val = float(val)
        elif item.get("class_code") is not None:
            numeric_val = float(item["class_code"])

        obs_date = None
        if item.get("period_start") and "T" in item["period_start"]:
            try:
                obs_date = datetime.fromisoformat(item["period_start"])
            except ValueError:
                pass

        records.append(
            EnvironmentalObservation(
                id=str(uuid4()),
                location_id=location_id,
                source=str(item.get("source") or "unknown"),
                metric=str(item.get("metric") or "unknown"),
                value=numeric_val,
                unit=str(item.get("unit")) if item.get("unit") else None,
                depth_or_layer=str(item.get("depth_or_layer")) if item.get("depth_or_layer") else None,
                observation_date=obs_date,
                period_start=str(item.get("period_start")) if item.get("period_start") else None,
                period_end=str(item.get("period_end")) if item.get("period_end") else None,
                latitude=float(item.get("latitude", latitude)),
                longitude=float(item.get("longitude", longitude)),
                raw_metadata=item.get("metadata") or {},
            )
        )
    db.add_all(records)
    db.commit()


@router.post("/data", response_model=EnvironmentalDataResponse)
def fetch_environmental_data(payload: EnvironmentalLocationRequest, db: Session = Depends(get_db)):
    try:
        latitude, longitude = validate_coordinates(payload.latitude, payload.longitude)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    result = collect_environmental_data(latitude, longitude, radius_km=payload.radius_km, db=db)
    persist_observations(db, latitude, longitude, result["observations"])
    return result


@router.get("/profile")
def read_profile(
    latitude: float | None = Query(default=None),
    longitude: float | None = Query(default=None),
    radius_km: float | None = Query(default=10.0),
    user_id: str = Depends(current_user_id),
    db: Session = Depends(get_db),
):
    try:
        if latitude is not None or longitude is not None:
            if latitude is None or longitude is None:
                raise HTTPException(status_code=422, detail="Both latitude and longitude are required for a real environmental profile lookup.")
            latitude, longitude = validate_coordinates(latitude, longitude)
            result = collect_environmental_data(latitude, longitude, radius_km=radius_km, db=db)
            persist_observations(db, latitude, longitude, result["observations"])
            return result["profile"]
        profile = get_profile(db, user_id)
        return serialize_profile(profile)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Environmental profile storage is unavailable.") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/profile", response_model=EnvironmentalProfileResponse, status_code=status.HTTP_201_CREATED)
def create_profile(payload: EnvironmentalProfilePayload, user_id: str = Depends(current_user_id), db: Session = Depends(get_db)):
    try:
        return serialize_profile(upsert_profile(db, user_id, payload))
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail="Environmental profile could not be saved.") from exc


@router.patch("/profile", response_model=EnvironmentalProfileResponse)
def update_profile(payload: EnvironmentalProfilePayload, user_id: str = Depends(current_user_id), db: Session = Depends(get_db)):
    try:
        if get_profile(db, user_id) is None:
            raise HTTPException(status_code=404, detail="No environmental profile available yet.")
        return serialize_profile(upsert_profile(db, user_id, payload))
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail="Environmental profile could not be updated.") from exc
