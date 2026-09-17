from __future__ import annotations

from typing import Any
from app.reasoning.schemas import MetricContext


def build_metric_contexts(
    profile: dict[str, Any],
    provider_status: dict[str, Any],
    user_context: dict[str, Any] | None = None,
) -> tuple[list[MetricContext], list[MetricContext]]:
    available: list[MetricContext] = []
    unavailable: list[MetricContext] = []

    soil = profile.get("soil", {})
    climate = profile.get("climate", {})
    land = profile.get("land", {})
    biodiversity = profile.get("biodiversity", {})

    # 1. Climate: Temperature
    if climate.get("temperature") is not None:
        period_str = None
        if isinstance(climate.get("temperature_period"), dict):
            p = climate["temperature_period"]
            period_str = f"{p.get('start', '')} to {p.get('end', '')}"
        available.append(
            MetricContext(
                metric="temperature",
                value=climate["temperature"],
                unit=climate.get("temperature_unit") or "C",
                period=period_str,
                source=climate.get("temperature_source") or "NASA POWER",
                availability="AVAILABLE",
            )
        )
    else:
        status_info = provider_status.get("nasa_power", {})
        unavailable.append(
            MetricContext(
                metric="temperature",
                availability="UNAVAILABLE",
                unavailability_reason=status_info.get("message") or "NASA POWER temperature data unavailable.",
            )
        )

    # 2. Climate: Rainfall
    if climate.get("rainfall") is not None:
        period_str = None
        if isinstance(climate.get("rainfall_period"), dict):
            p = climate["rainfall_period"]
            period_str = f"{p.get('start', '')} to {p.get('end', '')}"
        meta = {}
        if climate.get("accumulated_rainfall_mm") is not None:
            meta["accumulated_rainfall_mm"] = climate["accumulated_rainfall_mm"]
        available.append(
            MetricContext(
                metric="rainfall",
                value=climate["rainfall"],
                unit=climate.get("rainfall_unit") or "mm/day",
                period=period_str,
                source=climate.get("rainfall_source") or "NASA POWER",
                availability="AVAILABLE",
                metadata=meta,
            )
        )
    else:
        status_info = provider_status.get("nasa_power", {})
        unavailable.append(
            MetricContext(
                metric="rainfall",
                availability="UNAVAILABLE",
                unavailability_reason=status_info.get("message") or "NASA POWER rainfall data unavailable.",
            )
        )

    # 3. Land: Land Cover Class
    if land.get("land_cover") is not None:
        available.append(
            MetricContext(
                metric="land_cover_class",
                value=land["land_cover"],
                unit="class",
                source=land.get("source") or "ESA WorldCover 2021",
                availability="AVAILABLE",
                metadata={
                    "class_code": land.get("class_code"),
                    "tile_id": land.get("tile_id"),
                },
            )
        )
    else:
        status_info = provider_status.get("worldcover", {})
        unavailable.append(
            MetricContext(
                metric="land_cover_class",
                availability="UNAVAILABLE",
                unavailability_reason=status_info.get("message") or "ESA WorldCover data unavailable.",
            )
        )

    # 4. Biodiversity: Observed Species Richness & Observation Count
    if biodiversity.get("observed_species_richness") is not None:
        available.append(
            MetricContext(
                metric="observed_species_richness",
                value=biodiversity["observed_species_richness"],
                unit="species",
                source=biodiversity.get("observed_species_richness_source") or "GBIF",
                availability="AVAILABLE",
                metadata={
                    "observation_count": biodiversity.get("observation_count"),
                    "note": "Observed species richness from GBIF occurrence records; affected by sampling effort.",
                },
            )
        )
    else:
        status_info = provider_status.get("gbif", {})
        unavailable.append(
            MetricContext(
                metric="observed_species_richness",
                availability="UNAVAILABLE",
                unavailability_reason=status_info.get("message") or "GBIF occurrence data unavailable.",
            )
        )

    # 5. Soil: pH & Soil Organic Carbon
    if soil.get("ph") is not None:
        available.append(
            MetricContext(
                metric="soil_ph",
                value=soil["ph"],
                unit="pH",
                source=soil.get("source") or "ISRIC SoilGrids",
                availability="AVAILABLE",
                metadata={"depth": soil.get("depth")},
            )
        )
    else:
        status_info = provider_status.get("soilgrids", {})
        unavailable.append(
            MetricContext(
                metric="soil_ph",
                availability="UNAVAILABLE",
                unavailability_reason=(
                    f"SoilGrids unavailable: {status_info.get('message')}"
                    if (status_info.get("message") and "SoilGrids" not in status_info.get("message"))
                    else (status_info.get("message") or "ISRIC SoilGrids soil pH data unavailable upstream.")
                ),
            )
        )

    if soil.get("organic_carbon") is not None:
        available.append(
            MetricContext(
                metric="soil_organic_carbon",
                value=soil["organic_carbon"],
                unit="g/kg",
                source=soil.get("organic_carbon_source") or soil.get("source") or "ISRIC SoilGrids",
                availability="AVAILABLE",
                metadata={"depth": soil.get("organic_carbon_depth") or soil.get("depth")},
            )
        )
    else:
        status_info = provider_status.get("soilgrids", {})
        unavailable.append(
            MetricContext(
                metric="soil_organic_carbon",
                availability="UNAVAILABLE",
                unavailability_reason=(
                    f"SoilGrids unavailable: {status_info.get('message')}"
                    if (status_info.get("message") and "SoilGrids" not in status_info.get("message"))
                    else (status_info.get("message") or "ISRIC SoilGrids soil organic carbon data unavailable upstream.")
                ),
            )
        )

    # 6. User-provided context (e.g. crop, management, land use)
    if user_context:
        for k, v in user_context.items():
            if v is not None and v != "":
                available.append(
                    MetricContext(
                        metric=f"user_context_{k}",
                        value=v,
                        unit="context",
                        source="User Input",
                        availability="AVAILABLE",
                    )
                )

    return available, unavailable
