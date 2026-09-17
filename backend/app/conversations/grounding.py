from __future__ import annotations

from typing import Any
from sqlalchemy.orm import Session

from app.reasoning.schemas import ReasoningRequest, ReasoningResponse, LinkedEvidence
from app.reasoning.service import analyze_environment
from app.recommendations.schemas import RecommendationDto
from app.recommendations.recommendation_engine import generate_recommendations_from_reasoning

SYSTEM_INSTRUCTION = """You are TerraSage Grounded Conversational Intelligence.
Your role is to explain verified environmental data, multi-metric reasoning, and recommendations.
CRITICAL SCIENTIFIC INTEGRITY RULES:
1. Use ONLY the supplied TerraSage context as factual environmental information.
2. Do NOT invent measurements, soil values, rainfall values, species counts, scientific claims, citations, recommendations, confidence values, or impact percentages.
3. If required information is unavailable (such as ISRIC SoilGrids downtime), explicitly state that it is unavailable.
4. If asked about soil amendments when soil data is unavailable, state that on-site laboratory soil testing is mandatory before quantitative application.
5. Ground every explanation directly in the supplied multi-metric relationships and peer-reviewed FAO/IPCC literature."""


def run_grounded_scientific_pipeline(
    latitude: float,
    longitude: float,
    radius_km: float = 10.0,
    user_context: dict[str, Any] | None = None,
    text_context: str | None = None,
    db: Session | None = None,
) -> tuple[ReasoningResponse, list[RecommendationDto], list[LinkedEvidence], list[str]]:
    """Executes existing Chunk 4 reasoning and Chunk 5 recommendations without duplicate data collection."""
    if db is None:
        raise ValueError("Database session required for grounded scientific pipeline.")

    reasoning_req = ReasoningRequest(
        latitude=latitude,
        longitude=longitude,
        radius_km=radius_km,
        context=user_context,
        text_context=text_context,
    )

    # 1. Run Chunk 4 Multi-Metric Reasoning
    reasoning_res: ReasoningResponse = analyze_environment(db=db, request=reasoning_req)

    # 2. Run Chunk 5 Evidence-Backed Recommendations
    recommendations: list[RecommendationDto] = generate_recommendations_from_reasoning(reasoning_res)

    # 3. Collect all LinkedEvidence from relationships
    all_evidence: list[LinkedEvidence] = []
    seen_chunks = set()
    for rel in reasoning_res.relationships:
        for ev in rel.evidence:
            if ev.chunk_id not in seen_chunks:
                all_evidence.append(ev)
                seen_chunks.add(ev.chunk_id)

    # 4. Collect limitations
    limitations = list(reasoning_res.limitations)
    for rec in recommendations:
        for lim in rec.limitations:
            if lim not in limitations:
                limitations.append(lim)

    return reasoning_res, recommendations, all_evidence, limitations
