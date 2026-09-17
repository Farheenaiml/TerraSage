from __future__ import annotations

from typing import Iterable
from app.reasoning.schemas import LinkedEvidence


def validate_evidence_references(
    raw_referenced_ids: Iterable[str],
    available_evidence: list[LinkedEvidence],
) -> list[LinkedEvidence]:
    """Validates evidence IDs emitted by the LLM against actual LinkedEvidence from pgvector.

    Strips any hallucinated or non-existent chunk IDs.
    Returns only verified LinkedEvidence objects.
    """
    valid_map = {e.chunk_id: e for e in available_evidence}
    valid_map.update({e.document_id: e for e in available_evidence})

    verified: list[LinkedEvidence] = []
    seen = set()

    for ref in raw_referenced_ids:
        clean_ref = str(ref).strip().lower()
        for valid_id, ev in valid_map.items():
            if clean_ref == valid_id.lower() and valid_id not in seen:
                verified.append(ev)
                seen.add(valid_id)
                break

    return verified
