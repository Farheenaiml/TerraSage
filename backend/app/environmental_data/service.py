from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from app.environmental_data.cache import CacheRepository
from app.environmental_data.providers.gbif import GBIFProvider
from app.environmental_data.providers.nasa_power import NASAPOWERProvider
from app.environmental_data.providers.soilgrids import SoilGridsProvider
from app.environmental_data.providers.worldcover import WorldCoverProvider
from app.environmental_data.providers.air_quality import AirQualityProvider
from app.environmental_data.providers.hansen_forest_change import HansenForestChangeProvider
from app.environmental_data.schemas import EnvironmentalLocationRequest

PROVIDERS = {
    "nasa_power": NASAPOWERProvider(),
    "soilgrids": SoilGridsProvider(),
    "worldcover": WorldCoverProvider(),
    "gbif": GBIFProvider(),
    "air_quality": AirQualityProvider(),
    "hansen_forest_change": HansenForestChangeProvider(),
}


def validate_coordinates(latitude: float, longitude: float) -> tuple[float, float]:
    if latitude < -90 or latitude > 90:
        raise ValueError("Latitude must be between -90 and 90.")
    if longitude < -180 or longitude > 180:
        raise ValueError("Longitude must be between -180 and 180.")
    return latitude, longitude


def load_provider_data(provider_name: str, latitude: float, longitude: float, **options: Any) -> dict[str, Any]:
    provider = PROVIDERS.get(provider_name)
    if provider is None:
        raise ValueError(f"Unknown provider: {provider_name}")
    return provider.get_data(latitude, longitude, **options)


def collect_environmental_data(
    latitude: float,
    longitude: float,
    radius_km: float | None = 10.0,
    db: Session | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    latitude, longitude = validate_coordinates(latitude, longitude)
    provider_status: dict[str, Any] = {}
    observations: list[dict[str, Any]] = []
    cache = CacheRepository(db)

    for provider_name, provider in PROVIDERS.items():
        options: dict[str, Any] = {}
        if provider_name == "gbif":
            options["radius_km"] = radius_km or 10.0
        elif provider_name == "nasa_power":
            options["start_date"] = kwargs.get("start_date")
            options["end_date"] = kwargs.get("end_date")

        params = ",".join(f"{k}={v}" for k, v in sorted(options.items()))
        period = f"{options.get('start_date', '')}:{options.get('end_date', '')}"
        dataset_version = "2021" if provider_name == "worldcover" else "default"

        result = cache.get(provider_name, latitude, longitude, params, period, dataset_version)
        if result is None:
            result = provider.get_data(latitude, longitude, **options)
            # Only cache genuine successful responses, never errors or unavailable states
            if result.get("status") == "AVAILABLE":
                cache.set(provider_name, latitude, longitude, params, period, dataset_version, result)

        provider_status[provider_name] = {
            "provider": result.get("provider", getattr(provider, "provider_name", provider_name)),
            "status": result.get("status", "UNAVAILABLE"),
            "message": result.get("message"),
            "metadata": result.get("raw", {}),
        }

        for observation in result.get("observations", []):
            obs = dict(observation)
            obs.setdefault("latitude", latitude)
            obs.setdefault("longitude", longitude)
            obs.setdefault("retrieval_timestamp", datetime.now(timezone.utc).isoformat(timespec="seconds"))
            observations.append(obs)

    return {
        "location": {"latitude": latitude, "longitude": longitude, "radius_km": radius_km},
        "observations": observations,
        "provider_status": provider_status,
        "profile": build_environmental_profile(latitude, longitude, observations),
    }


def build_environmental_profile(latitude: float, longitude: float, observations: list[dict[str, Any]]) -> dict[str, Any]:
    soil: dict[str, Any] = {}
    climate: dict[str, Any] = {}
    land: dict[str, Any] = {}
    biodiversity: dict[str, Any] = {}
    human_impact: dict[str, Any] = {}

    annual_temp = None
    latest_temp = None
    annual_rain = None
    latest_rain = None

    for item in observations:
        metric = item.get("metric")
        value = item.get("value")
        meta = item.get("metadata") or {}

        if metric == "soil_pH":
            soil["ph"] = value
            soil["depth"] = item.get("depth_or_layer")
            soil["source"] = item.get("source")
        elif metric == "soil_organic_carbon":
            soil["organic_carbon"] = value
            soil["organic_carbon_depth"] = item.get("depth_or_layer")
            soil["organic_carbon_source"] = item.get("source")
        elif metric == "temperature":
            if meta.get("is_annual_average"):
                annual_temp = item
            else:
                latest_temp = item
        elif metric == "rainfall":
            if meta.get("is_annual_average"):
                annual_rain = item
            else:
                latest_rain = item
        elif metric == "land_cover_class":
            land["land_cover"] = value
            land["source"] = item.get("source")
            land["class_code"] = meta.get("land_cover_class_code")
            land["tile_id"] = meta.get("tile_id")
        elif metric == "observation_count":
            biodiversity["observation_count"] = value
            biodiversity["observation_count_source"] = item.get("source")
        elif metric == "distinct_species_count":
            biodiversity["observed_species_richness"] = value
            biodiversity["observed_species_richness_source"] = item.get("source")
        elif metric == "pm2_5":
            human_impact["pm2_5"] = value
            human_impact["pm2_5_unit"] = item.get("unit") or "ug/m3"
            human_impact["pm2_5_source"] = item.get("source")
            human_impact["pm2_5_period"] = {"start": item.get("period_start"), "end": item.get("period_end")}
            if meta.get("european_aqi") is not None:
                human_impact["european_aqi"] = meta["european_aqi"]
            if meta.get("us_aqi") is not None:
                human_impact["us_aqi"] = meta["us_aqi"]
        elif metric == "pm10":
            human_impact["pm10"] = value
            human_impact["pm10_unit"] = item.get("unit") or "ug/m3"
            human_impact["pm10_source"] = item.get("source")
        elif metric == "air_quality_index":
            human_impact["aqi"] = value
        elif metric == "annual_tree_cover_loss":
            human_impact["annual_tree_cover_loss_ha"] = value
            human_impact["annual_tree_cover_loss_unit"] = item.get("unit") or "ha"
            human_impact["forest_loss_source"] = item.get("source")
            human_impact["forest_loss_year"] = meta.get("year")

    chosen_temp = annual_temp or latest_temp
    if chosen_temp:
        climate["temperature"] = chosen_temp.get("value")
        climate["temperature_unit"] = chosen_temp.get("unit") or "C"
        climate["temperature_period"] = {"start": chosen_temp.get("period_start"), "end": chosen_temp.get("period_end")}
        climate["temperature_source"] = chosen_temp.get("source")

    chosen_rain = annual_rain or latest_rain
    if chosen_rain:
        climate["rainfall"] = chosen_rain.get("value")
        climate["rainfall_unit"] = chosen_rain.get("unit") or "mm/day"
        climate["rainfall_period"] = {"start": chosen_rain.get("period_start"), "end": chosen_rain.get("period_end")}
        climate["rainfall_source"] = chosen_rain.get("source")
        if chosen_rain.get("metadata", {}).get("accumulated_precipitation_mm") is not None:
            climate["accumulated_rainfall_mm"] = chosen_rain["metadata"]["accumulated_precipitation_mm"]

    return {
        "soil": soil,
        "climate": climate,
        "land": land,
        "biodiversity": biodiversity,
        "human_impact": human_impact,
        "location": {"latitude": latitude, "longitude": longitude},
    }
