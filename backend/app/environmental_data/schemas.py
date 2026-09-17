from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class EnvironmentalLocationRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float | None = Field(default=10.0, ge=0.1, le=1000)
    location_name: str | None = None
    country: str | None = None
    region: str | None = None


class EnvironmentalObservation(BaseModel):
    metric: str
    value: float | int | str | None = None
    unit: str | None = None
    source: str
    latitude: float | None = None
    longitude: float | None = None
    depth_or_layer: str | None = None
    period_start: str | None = None
    period_end: str | None = None
    retrieval_timestamp: str | None = None
    metadata: dict[str, Any] = {}


class ProviderStatus(BaseModel):
    provider: str
    status: str
    message: str | None = None
    metadata: dict[str, Any] = {}


class EnvironmentalDataResponse(BaseModel):
    location: dict[str, Any]
    observations: list[EnvironmentalObservation]
    provider_status: dict[str, ProviderStatus]
    profile: dict[str, Any]
