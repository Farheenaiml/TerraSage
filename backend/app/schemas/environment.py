from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ApiModel(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True, alias_generator=lambda value: ''.join([value.split('_')[0], *[part.capitalize() for part in value.split('_')[1:]]]))


class SoilMetricPayload(ApiModel):
    ph: float | None = Field(default=None, ge=0, le=14)
    organic_carbon: float | None = Field(default=None, ge=0)
    moisture: float | None = Field(default=None, ge=0, le=100)


class ClimateMetricPayload(ApiModel):
    temperature: float | None = None
    rainfall: float | None = Field(default=None, ge=0)


class LandMetricPayload(ApiModel):
    land_use: str | None = Field(default=None, max_length=200)
    land_cover: str | None = Field(default=None, max_length=200)


class BiodiversityMetricPayload(ApiModel):
    species_richness: float | None = Field(default=None, ge=0)
    habitat_diversity: float | None = Field(default=None, ge=0)


class HumanImpactMetricPayload(ApiModel):
    pollution: float | None = Field(default=None, ge=0)
    deforestation: float | None = Field(default=None, ge=0)


class EnvironmentalProfilePayload(ApiModel):
    region: str | None = Field(default=None, max_length=200)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    soil: SoilMetricPayload | None = None
    climate: ClimateMetricPayload | None = None
    land: LandMetricPayload | None = None
    biodiversity: BiodiversityMetricPayload | None = None
    human_impact: HumanImpactMetricPayload | None = None


class EnvironmentalProfileResponse(EnvironmentalProfilePayload):
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime
    available_fields: list[str]
    missing_fields: list[str]


class EnvironmentalLocationRequest(ApiModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    radius_km: float | None = Field(default=10.0, ge=0.1, le=1000)
    location_name: str | None = Field(default=None, max_length=200)
    country: str | None = Field(default=None, max_length=200)
    region: str | None = Field(default=None, max_length=200)


class EnvironmentalDataObservation(ApiModel):
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


class EnvironmentalDataResponse(ApiModel):
    location: dict[str, Any]
    observations: list[EnvironmentalDataObservation]
    provider_status: dict[str, Any]
    profile: dict[str, Any]


class PlaceholderCollections(ApiModel):
    recent_analyses: list[Any] = []
    recommendations: list[Any] = []
    evidence_summary: dict[str, Any] = {"total": 0, "recentCount": 0, "byType": {}}


class DashboardResponse(ApiModel):
    profile: EnvironmentalProfileResponse | None
    available_fields: list[str]
    missing_fields: list[str]
    recent_analyses: list[Any]
    recommendations: list[Any]
    evidence_summary: dict[str, Any]

    @model_validator(mode="before")
    @classmethod
    def copy_profile_field_lists(cls, values: Any) -> Any:
        return values
