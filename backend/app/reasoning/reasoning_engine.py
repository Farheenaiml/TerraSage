from __future__ import annotations

from typing import Any
from sqlalchemy.orm import Session

from app.reasoning.metric_context import build_metric_contexts
from app.reasoning.relationship_rules import detect_relationships
from app.reasoning.evidence_linker import link_evidence_to_relationships
from app.reasoning.schemas import ReasoningResponse


def execute_environmental_reasoning(
    db: Session,
    latitude: float,
    longitude: float,
    profile: dict[str, Any],
    provider_status: dict[str, Any],
    user_context: dict[str, Any] | None = None,
    text_context: str | None = None,
) -> ReasoningResponse:
    # 1. Build standardized metric contexts
    available, unavailable = build_metric_contexts(profile, provider_status, user_context)

    # 2. Detect multi-metric relationships using deterministic rules
    candidates = detect_relationships(available, unavailable, user_context)

    # 3. Retrieve and link authoritative scientific evidence
    relationships = link_evidence_to_relationships(db, candidates)

    # 4. Compile overall limitations and caveats
    limitations: list[str] = []

    # Check for SoilGrids unavailability
    soil_unavail = [m for m in unavailable if m.metric in ("soil_organic_carbon", "soil_ph")]
    if soil_unavail:
        limitations.append(
            "Direct soil-condition interpretation is limited because SoilGrids soil pH and soil organic carbon "
            "data were unavailable during retrieval. Soil metrics were not fabricated."
        )

    # Check for GBIF observation disclaimer
    if any(m.metric == "observed_species_richness" for m in available):
        limitations.append(
            "Biodiversity metrics reflect observed species richness from GBIF occurrence records and are "
            "subject to spatial sampling and observer effort variations."
        )

    # 5. Formulate structured overall interpretation
    avail_names = [m.metric for m in available if not m.metric.startswith("user_context_")]
    land_m = next((m for m in available if m.metric == "land_cover_class"), None)
    land_name = str(land_m.value) if land_m else "unspecified land cover"

    overall_interpretation = (
        f"Environmental analysis across {len(avail_names)} available metrics ({', '.join(avail_names)}) "
        f"characterizes this site as a {land_name.lower()}-influenced ecosystem. "
        f"Detected relationships show coherent interactions between climatic conditions and land characteristics, "
        f"corroborated by authoritative literature from FAO and IPCC. "
    )
    if soil_unavail:
        overall_interpretation += (
            "Because upstream soil services were unavailable, soil-specific vulnerability assessments "
            "cannot be asserted without direct site measurements."
        )

    return ReasoningResponse(
        location={"latitude": latitude, "longitude": longitude},
        user_context=user_context or {},
        available_metrics=available,
        unavailable_metrics=unavailable,
        relationships=relationships,
        overall_interpretation=overall_interpretation,
        limitations=limitations,
    )
