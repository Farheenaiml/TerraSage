import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.database import SessionLocal
from app.reasoning.schemas import MetricContext, ReasoningRequest
from app.reasoning.metric_context import build_metric_contexts
from app.reasoning.relationship_rules import detect_relationships, DetectedRelationshipCandidate
from app.reasoning.evidence_linker import link_evidence_to_relationships
from app.reasoning.reasoning_engine import execute_environmental_reasoning
from app.reasoning.service import analyze_environment


def test_metric_context_normalization_and_availability():
    profile = {
        "climate": {"temperature": 26.6, "rainfall": 9.16, "accumulated_rainfall_mm": 3343.4},
        "land": {"land_cover": "Built-up", "class_code": 50},
        "biodiversity": {"observed_species_richness": 2417, "observation_count": 338380},
        "soil": {},  # Empty because SoilGrids unavailable
    }
    provider_status = {
        "nasa_power": {"status": "AVAILABLE"},
        "worldcover": {"status": "AVAILABLE"},
        "gbif": {"status": "AVAILABLE"},
        "soilgrids": {"status": "UNAVAILABLE", "message": "Upstream 500 error"},
    }
    available, unavailable = build_metric_contexts(profile, provider_status)

    avail_names = {m.metric for m in available}
    unavail_names = {m.metric for m in unavailable}

    assert "temperature" in avail_names
    assert "rainfall" in avail_names
    assert "land_cover_class" in avail_names
    assert "observed_species_richness" in avail_names

    assert "soil_organic_carbon" in unavail_names
    assert "soil_ph" in unavail_names

    soc_metric = next(m for m in unavailable if m.metric == "soil_organic_carbon")
    assert soc_metric.availability == "UNAVAILABLE"
    assert soc_metric.value is None
    assert "SoilGrids" in soc_metric.unavailability_reason


def test_unavailable_soilgrids_never_converts_to_zero():
    profile = {"soil": {}, "climate": {}, "land": {}, "biodiversity": {}}
    provider_status = {"soilgrids": {"status": "UNAVAILABLE"}}
    available, unavailable = build_metric_contexts(profile, provider_status)

    for m in unavailable:
        assert m.value is not 0
        assert m.value is None


def test_three_metric_relationship_detection():
    available = [
        MetricContext(metric="temperature", value=26.6, unit="C"),
        MetricContext(metric="rainfall", value=9.16, unit="mm/day", metadata={"accumulated_precipitation_mm": 3343.4}),
        MetricContext(metric="land_cover_class", value="Built-up", unit="class"),
        MetricContext(metric="observed_species_richness", value=2417, unit="species", metadata={"observation_count": 338380}),
    ]
    unavailable = [
        MetricContext(metric="soil_organic_carbon", availability="UNAVAILABLE"),
        MetricContext(metric="soil_ph", availability="UNAVAILABLE"),
    ]
    candidates = detect_relationships(available, unavailable)

    # Should detect 3-metric or 4-metric relationships
    assert len(candidates) >= 2
    assert all(c.is_multi_metric for c in candidates)
    for c in candidates:
        assert len(c.metrics) >= 3


def test_two_metric_fallback_labeling():
    # Only 2 metrics available
    available = [
        MetricContext(metric="temperature", value=20.5, unit="C"),
        MetricContext(metric="rainfall", value=1.5, unit="mm/day"),
    ]
    unavailable = [
        MetricContext(metric="land_cover_class", availability="UNAVAILABLE"),
        MetricContext(metric="observed_species_richness", availability="UNAVAILABLE"),
        MetricContext(metric="soil_organic_carbon", availability="UNAVAILABLE"),
    ]
    candidates = detect_relationships(available, unavailable)

    assert len(candidates) == 1
    cand = candidates[0]
    assert not cand.is_multi_metric
    assert cand.fallback_label == "Limited 2-metric analysis"
    assert len(cand.metrics) == 2


def test_agricultural_soil_carbon_relationship_detection():
    # When soil organic carbon is available
    available = [
        MetricContext(metric="temperature", value=24.0, unit="C"),
        MetricContext(metric="rainfall", value=3.2, unit="mm/day"),
        MetricContext(metric="land_cover_class", value="Cropland", unit="class"),
        MetricContext(metric="soil_organic_carbon", value=12.5, unit="g/kg"),
    ]
    unavailable = []
    candidates = detect_relationships(available, unavailable)

    rel_types = {c.relationship_type for c in candidates}
    assert "soil_carbon_moisture_resilience" in rel_types
    soc_cand = next(c for c in candidates if c.relationship_type == "soil_carbon_moisture_resilience")
    assert "soil_organic_carbon" in soc_cand.metrics
    assert "rainfall" in soc_cand.metrics
    assert "land_cover_class" in soc_cand.metrics


def test_evidence_linking_with_pgvector():
    if SessionLocal is None:
        pytest.skip("Database not configured")
    db = SessionLocal()

    candidate = DetectedRelationshipCandidate(
        relationship_id="test_rel",
        relationship_type="test_type",
        title="Test Relationship",
        metrics=["temperature", "rainfall", "land_cover_class"],
        query="climate land use rainfall water availability",
        interpretation="Test interpretation",
        is_multi_metric=True,
    )

    relationships = link_evidence_to_relationships(db, [candidate])
    assert len(relationships) == 1
    rel = relationships[0]
    assert rel.evidence_status == "supported"
    assert len(rel.evidence) >= 1
    ev = rel.evidence[0]
    assert ev.document_id is not None
    assert ev.chunk_id is not None
    assert ev.retrieval_score > 0
    assert len(ev.excerpt) > 10
    db.close()


def test_insufficient_evidence_handling():
    if SessionLocal is None:
        pytest.skip("Database not configured")
    db = SessionLocal()

    # Query for completely unrelated/nonsense query that won't match environmental literature
    candidate = DetectedRelationshipCandidate(
        relationship_id="test_nonsense",
        relationship_type="test_type",
        title="Nonsense Relationship",
        metrics=["quantum_entanglement", "blockchain"],
        query="quantum superconductor silicon wafer qubit gate",
        interpretation="Unsupported claim",
        is_multi_metric=False,
    )

    relationships = link_evidence_to_relationships(db, [candidate])
    assert relationships[0].evidence_status == "insufficient_evidence"
    db.close()


def test_complete_reasoning_engine_execution():
    if SessionLocal is None:
        pytest.skip("Database not configured")
    db = SessionLocal()

    profile = {
        "climate": {"temperature": 26.61, "rainfall": 9.16, "accumulated_rainfall_mm": 3343.4},
        "land": {"land_cover": "Built-up", "class_code": 50, "tile_id": "ESA_WorldCover_10m_2021_v200_N18E072"},
        "biodiversity": {"observed_species_richness": 2417, "observation_count": 338380},
        "soil": {},
    }
    provider_status = {
        "nasa_power": {"status": "AVAILABLE"},
        "worldcover": {"status": "AVAILABLE"},
        "gbif": {"status": "AVAILABLE"},
        "soilgrids": {"status": "UNAVAILABLE", "message": "Upstream paused"},
    }

    response = execute_environmental_reasoning(
        db=db,
        latitude=19.076,
        longitude=72.8777,
        profile=profile,
        provider_status=provider_status,
    )

    assert response.location["latitude"] == 19.076
    assert len(response.available_metrics) == 4
    assert len(response.unavailable_metrics) >= 2
    assert len(response.relationships) >= 2
    assert any("SoilGrids" in lim for lim in response.limitations)
    assert any("GBIF" in lim for lim in response.limitations)
    assert "built-up-influenced" in response.overall_interpretation
    db.close()


def test_reasoning_api_endpoint():
    client = TestClient(app)
    resp = client.post("/api/reasoning/analyze", json={"latitude": 19.076, "longitude": 72.8777})
    assert resp.status_code == 200
    data = resp.json()

    assert "location" in data
    assert "availableMetrics" in data
    assert "unavailableMetrics" in data
    assert "relationships" in data
    assert "overallInterpretation" in data
    assert "limitations" in data

    # Check that relationships have linked evidence from ingested documents
    relationships = data["relationships"]
    assert len(relationships) >= 1
    first_rel = relationships[0]
    assert first_rel["evidenceStatus"] == "supported"
    assert len(first_rel["evidence"]) >= 1


def test_reasoning_api_coordinate_validation():
    client = TestClient(app)
    resp = client.post("/api/reasoning/analyze", json={"latitude": 999.0, "longitude": 72.8777})
    assert resp.status_code == 422
