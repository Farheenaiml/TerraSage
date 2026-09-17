from sqlalchemy.orm import Session

from app.models import (
    BiodiversityMetric,
    ClimateMetric,
    EnvironmentalProfile,
    HumanImpactMetric,
    LandMetric,
    SoilMetric,
)
from app.repositories.environment_repository import EnvironmentRepository
from app.schemas.environment import EnvironmentalProfilePayload

CORE_FIELDS = {
    "soil.ph": lambda profile: profile.soil and profile.soil.ph,
    "soil.organicCarbon": lambda profile: profile.soil and profile.soil.organic_carbon,
    "soil.moisture": lambda profile: profile.soil and profile.soil.moisture,
    "climate.temperature": lambda profile: profile.climate and profile.climate.temperature,
    "climate.rainfall": lambda profile: profile.climate and profile.climate.rainfall,
    "land.landUse": lambda profile: profile.land and profile.land.land_use,
    "land.landCover": lambda profile: profile.land and profile.land.land_cover,
    "biodiversity.speciesRichness": lambda profile: profile.biodiversity and profile.biodiversity.species_richness,
    "biodiversity.habitatDiversity": lambda profile: profile.biodiversity and profile.biodiversity.habitat_diversity,
    "humanImpact.pollution": lambda profile: profile.human_impact and profile.human_impact.pollution,
    "humanImpact.deforestation": lambda profile: profile.human_impact and profile.human_impact.deforestation,
}


def field_status(profile: EnvironmentalProfile | None) -> tuple[list[str], list[str]]:
    if profile is None:
        return [], list(CORE_FIELDS)
    available = [name for name, getter in CORE_FIELDS.items() if getter(profile) is not None]
    return available, [name for name in CORE_FIELDS if name not in available]


def apply_payload(profile: EnvironmentalProfile, payload: EnvironmentalProfilePayload) -> EnvironmentalProfile:
    data = payload.model_dump(exclude_unset=True, by_alias=False)
    for field in ("region", "latitude", "longitude"):
        if field in data:
            setattr(profile, field, data[field])

    metric_types = {
        "soil": (SoilMetric, "soil"),
        "climate": (ClimateMetric, "climate"),
        "land": (LandMetric, "land"),
        "biodiversity": (BiodiversityMetric, "biodiversity"),
        "human_impact": (HumanImpactMetric, "human_impact"),
    }
    for key, (model, relationship) in metric_types.items():
        if key not in data:
            continue
        metric = getattr(profile, relationship) or model()
        for field, value in (data[key] or {}).items():
            setattr(metric, field, value)
        setattr(profile, relationship, metric)
    return profile


def get_profile(db: Session, user_id: str) -> EnvironmentalProfile | None:
    return EnvironmentRepository(db).get_profile(user_id)


def upsert_profile(db: Session, user_id: str, payload: EnvironmentalProfilePayload) -> EnvironmentalProfile:
    repository = EnvironmentRepository(db)
    repository.ensure_user(user_id)
    profile = repository.get_profile(user_id) or EnvironmentalProfile(user_id=user_id)
    return repository.save_profile(apply_payload(profile, payload))
