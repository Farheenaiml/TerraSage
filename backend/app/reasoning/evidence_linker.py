from __future__ import annotations

import re
from typing import Any
from sqlalchemy.orm import Session

from app.knowledge.retrieval import retrieve
from app.reasoning.relationship_rules import DetectedRelationshipCandidate
from app.reasoning.schemas import EnvironmentalRelationship, LinkedEvidence

# Minimum cosine similarity threshold to consider evidence relevant
EVIDENCE_SIMILARITY_THRESHOLD = 0.35

METRIC_TERMS = {
    "temperature": ["temperature", "warming", "thermal", "heat"],
    "rainfall": ["rainfall", "precipitation", "water", "moisture", "drought"],
    "land_cover_class": ["land cover", "land use", "built-up", "urban", "cropland", "vegetation", "forest"],
    "observed_species_richness": ["biodiversity", "species", "taxa", "richness", "organism"],
    "soil_organic_carbon": ["organic carbon", "soil carbon", "soc", "humus"],
    "soil_ph": ["ph", "acidity", "alkalinity"],
}


def link_evidence_to_relationships(
    db: Session,
    candidates: list[DetectedRelationshipCandidate],
) -> list[EnvironmentalRelationship]:
    relationships: list[EnvironmentalRelationship] = []

    for candidate in candidates:
        # Retrieve top 3 relevant chunks from existing knowledge base
        rag_results = retrieve(db, candidate.query, top_k=3, metrics=candidate.metrics)
        linked: list[LinkedEvidence] = []

        for score, document, chunk, matched in rag_results:
            if score < EVIDENCE_SIMILARITY_THRESHOLD:
                continue

            content = (chunk.content or "").strip()
            if not content:
                continue

            # Quality control check: ensure chunk mentions at least one relevant metric concept
            content_lower = content.lower()
            relevant = False
            for m in candidate.metrics:
                terms = METRIC_TERMS.get(m, [m])
                if any(t in content_lower for t in terms):
                    relevant = True
                    break

            if not relevant:
                continue

            # Clean excerpt for presentation
            clean_excerpt = re.sub(r"\s+", " ", content)[:400] + ("..." if len(content) > 400 else "")

            linked.append(
                LinkedEvidence(
                    document_id=document.id,
                    chunk_id=chunk.id,
                    source=document.organization or document.title,
                    title=document.title,
                    organization=document.organization,
                    publication_year=document.year,
                    excerpt=clean_excerpt,
                    retrieval_score=round(score, 4),
                    source_url=document.source_url,
                    matched_metrics=matched,
                )
            )

        evidence_status = "supported" if len(linked) >= 1 else "insufficient_evidence"

        relationships.append(
            EnvironmentalRelationship(
                relationship_id=candidate.relationship_id,
                relationship_type=candidate.relationship_type,
                title=candidate.title,
                metrics=candidate.metrics,
                metrics_count=len(candidate.metrics),
                is_multi_metric=candidate.is_multi_metric,
                fallback_label=candidate.fallback_label,
                interpretation=candidate.interpretation,
                evidence_status=evidence_status,
                evidence=linked,
                limitations=candidate.limitations,
            )
        )

    return relationships
