from __future__ import annotations

from typing import Any
from app.reasoning.schemas import MetricContext


class DetectedRelationshipCandidate:
    def __init__(
        self,
        relationship_id: str,
        relationship_type: str,
        title: str,
        metrics: list[str],
        query: str,
        interpretation: str,
        is_multi_metric: bool = True,
        fallback_label: str | None = None,
        limitations: list[str] | None = None,
    ):
        self.relationship_id = relationship_id
        self.relationship_type = relationship_type
        self.title = title
        self.metrics = metrics
        self.query = query
        self.interpretation = interpretation
        self.is_multi_metric = is_multi_metric
        self.fallback_label = fallback_label
        self.limitations = limitations or []


def detect_relationships(
    available_metrics: list[MetricContext],
    unavailable_metrics: list[MetricContext],
    user_context: dict[str, Any] | None = None,
) -> list[DetectedRelationshipCandidate]:
    candidates: list[DetectedRelationshipCandidate] = []
    avail_dict = {m.metric: m for m in available_metrics}
    unavail_dict = {m.metric: m for m in unavailable_metrics}

    has_temp = "temperature" in avail_dict
    has_rain = "rainfall" in avail_dict
    has_land = "land_cover_class" in avail_dict
    has_bio = "observed_species_richness" in avail_dict
    has_soc = "soil_organic_carbon" in avail_dict
    has_ph = "soil_ph" in avail_dict

    temp_val = avail_dict["temperature"].value if has_temp else None
    rain_val = avail_dict["rainfall"].value if has_rain else None
    land_val = str(avail_dict["land_cover_class"].value) if has_land else None
    bio_val = avail_dict["observed_species_richness"].value if has_bio else None
    soc_val = avail_dict["soil_organic_carbon"].value if has_soc else None

    # RULE 1: Climate + Land Cover + Biodiversity (4-Metric analysis when all 4 are present)
    if has_temp and has_rain and has_land and has_bio:
        if land_val == "Built-up":
            interp = (
                f"The co-occurrence of mean temperature ({temp_val}°C), "
                f"precipitation rate ({rain_val} mm/day), and Built-up land cover "
                f"defines an urbanized environmental regime. Within this setting, "
                f"the observed species richness ({bio_val} species from GBIF occurrences) "
                f"is consistent with urban-adapted, synanthropic, and remnant habitat-associated taxa. "
                f"Urban thermal dynamics and surface impermeability may influence local microclimate "
                f"and species assemblages relative to adjacent natural vegetation."
            )
            query = "climate urban land use biodiversity species richness"
        else:
            interp = (
                f"The co-occurrence of mean temperature ({temp_val}°C), "
                f"precipitation rate ({rain_val} mm/day), and {land_val} land cover "
                f"establishes a localized bioclimatic context. Under these conditions, "
                f"observed species richness ({bio_val} species from GBIF occurrence records) "
                f"reflects the habitat availability and ecological niche space supported by this land-cover type."
            )
            query = f"climate land cover {land_val} biodiversity species richness"

        candidates.append(
            DetectedRelationshipCandidate(
                relationship_id="rel_climate_land_biodiversity",
                relationship_type="climate_land_biodiversity_context",
                title="Climate, Land-Cover & Biodiversity Context",
                metrics=["temperature", "rainfall", "land_cover_class", "observed_species_richness"],
                query=query,
                interpretation=interp,
                is_multi_metric=True,
                limitations=[
                    "Observed species richness is derived from GBIF occurrence records and is subject to geographic observation bias."
                ],
            )
        )

    # RULE 2: Climate + Land-Cover Moisture Context (3-Metric analysis)
    if has_temp and has_rain and has_land:
        rain_accum = avail_dict["rainfall"].metadata.get("accumulated_precipitation_mm")
        accum_note = f" (accumulated annual precipitation ~{rain_accum} mm)" if rain_accum else ""
        interp = (
            f"The combination of thermal regime ({temp_val}°C) and precipitation ({rain_val} mm/day){accum_note} "
            f"governs atmospheric evaporative demand and moisture availability for the {land_val} surface. "
            f"In {land_val.lower()} areas, these climatic factors influence hydrological balance, "
            f"runoff dynamics, and vegetative moisture retention."
        )
        candidates.append(
            DetectedRelationshipCandidate(
                relationship_id="rel_climate_land_moisture",
                relationship_type="climate_land_water_dynamics",
                title="Climate & Land-Cover Hydrological Dynamics",
                metrics=["temperature", "rainfall", "land_cover_class"],
                query=f"temperature rainfall {land_val} moisture water balance",
                interpretation=interp,
                is_multi_metric=True,
            )
        )

    # RULE 3: Soil Carbon + Rainfall + Agricultural Land Cover (3-Metric analysis when SOC is available)
    if has_soc and has_rain and has_land:
        interp = (
            f"Soil organic carbon ({soc_val} g/kg) and precipitation ({rain_val} mm/day) "
            f"jointly modulate soil structure, aggregate stability, and infiltration capacity in {land_val} systems. "
            f"Higher organic carbon is scientifically associated with improved water-holding capacity and resilience against moisture stress."
        )
        candidates.append(
            DetectedRelationshipCandidate(
                relationship_id="rel_soil_water_resilience",
                relationship_type="soil_carbon_moisture_resilience",
                title="Soil Carbon & Moisture Resilience",
                metrics=["soil_organic_carbon", "rainfall", "land_cover_class"],
                query="soil organic carbon rainfall agriculture water retention",
                interpretation=interp,
                is_multi_metric=True,
            )
        )

    # RULE 4: Land Cover + Habitat Diversity + Observed Biodiversity (3-Metric analysis when observation count present)
    if has_land and has_bio and "observed_species_richness" in avail_dict:
        obs_count = avail_dict["observed_species_richness"].metadata.get("observation_count")
        if obs_count is not None:
            interp = (
                f"Under {land_val} land cover, the {obs_count} recorded GBIF occurrences "
                f"yielded {bio_val} distinct observed species. Scientific literature demonstrates that "
                f"habitat structure associated with {land_val.lower()} cover strongly dictates ecological niche availability, "
                f"though total observed richness is influenced by collection effort in the surveyed radius."
            )
            candidates.append(
                DetectedRelationshipCandidate(
                    relationship_id="rel_habitat_species_richness",
                    relationship_type="land_cover_habitat_biodiversity",
                    title="Land-Cover Habitat & Species Representation",
                    metrics=["land_cover_class", "observed_species_richness", "gbif_observation_count"],
                    query=f"land cover {land_val} habitat diversity species richness",
                    interpretation=interp,
                    is_multi_metric=True,
                    limitations=[
                        "GBIF occurrence records reflect sampling intensity and observer density rather than an exhaustive biological census."
                    ],
                )
            )

    # RULE 5: Two-Metric Fallback (explicitly labeled when 3 metrics not possible)
    if not candidates:
        if has_temp and has_rain:
            candidates.append(
                DetectedRelationshipCandidate(
                    relationship_id="rel_climate_temperature_rainfall",
                    relationship_type="climate_temperature_precipitation_coupling",
                    title="Temperature & Precipitation Coupling",
                    metrics=["temperature", "rainfall"],
                    query="temperature precipitation climate interactions",
                    interpretation=(
                        f"Mean temperature ({temp_val}°C) and precipitation ({rain_val} mm/day) "
                        f"describe the fundamental thermodynamic state of the local atmosphere."
                    ),
                    is_multi_metric=False,
                    fallback_label="Limited 2-metric analysis",
                    limitations=["Analysis is limited to 2 metrics because land-cover and biodiversity data were not available."],
                )
            )

    return candidates
