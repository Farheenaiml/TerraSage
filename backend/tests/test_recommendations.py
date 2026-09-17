from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.config import settings
from app.core.database import Base
from app.reasoning.schemas import (
    ReasoningResponse,
    MetricContext,
    EnvironmentalRelationship,
    LinkedEvidence,
)
from app.recommendations.schemas import RecommendationDto
from app.recommendations.recommendation_engine import generate_recommendations_from_reasoning
from app.recommendations.service import (
    generate_recommendations,
    list_recommendations,
    get_recommendation,
    update_recommendation_status,
)
from app.recommendations.schemas import RecommendationGenerateRequest


@pytest.fixture
def db_session():
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


def test_recommendation_generation_directly_from_reasoning():
    """Verifies recommendations are derived directly from ReasoningResponse with LinkedEvidence."""
    evidence_item = LinkedEvidence(
        document_id="doc-fao-123",
        chunk_id="chunk-fao-456",
        source="FAO",
        title="State of Knowledge of Soil Biodiversity",
        organization="Food and Agriculture Organization",
        publication_year=2020,
        excerpt="Agroforestry and crop diversification enhance structural niches...",
        retrieval_score=0.58,
        source_url="https://example.com/fao",
        matched_metrics=["observed_species_richness", "temperature"],
    )

    relationship = EnvironmentalRelationship(
        relationship_id="rel-crop-bio-1",
        relationship_type="climate_land_biodiversity_context",
        title="Climate, Land-Cover & Biodiversity Context",
        metrics=["temperature", "rainfall", "land_cover_class", "observed_species_richness"],
        metrics_count=4,
        is_multi_metric=True,
        interpretation="Thermal regime and precipitation interact with Cropland cover to shape species richness.",
        evidence_status="supported",
        evidence=[evidence_item],
        limitations=["Subject to GBIF sampling effort."],
    )

    reasoning_res = ReasoningResponse(
        location={"latitude": 19.8, "longitude": 74.4, "radius_km": 10.0},
        available_metrics=[
            MetricContext(metric="temperature", value=24.8, unit="C", availability="AVAILABLE"),
            MetricContext(metric="rainfall", value=2.73, unit="mm/day", availability="AVAILABLE"),
            MetricContext(metric="land_cover_class", value="Cropland class", availability="AVAILABLE"),
            MetricContext(metric="observed_species_richness", value=121, unit="species", availability="AVAILABLE"),
        ],
        unavailable_metrics=[
            MetricContext(metric="soil_organic_carbon", availability="UNAVAILABLE", unavailability_reason="SoilGrids down"),
            MetricContext(metric="soil_ph", availability="UNAVAILABLE", unavailability_reason="SoilGrids down"),
        ],
        relationships=[relationship],
        overall_interpretation="Cropland agricultural ecosystem with verified interactions.",
        limitations=["Direct soil metrics unavailable."],
    )

    recs = generate_recommendations_from_reasoning(reasoning_res)

    assert len(recs) >= 1
    agro_rec = next((r for r in recs if r.category == "agroforestry"), None)
    assert agro_rec is not None
    assert "Agroforestry" in agro_rec.title
    assert agro_rec.confidence == "high"
    # Scientific integrity: NO fake confidence percentage
    assert agro_rec.confidence_score is None
    assert len(agro_rec.confidence_rationale) > 0
    # Linked evidence strictly inherited
    assert len(agro_rec.evidence) == 1
    assert agro_rec.evidence[0].document_id == "doc-fao-123"
    assert agro_rec.relationship_id == "rel-crop-bio-1"


def test_honest_soil_diagnostic_recommendation_when_soil_unavailable():
    """Verifies honest diagnostic action without fabricated rates when SoilGrids is unavailable."""
    reasoning_res = ReasoningResponse(
        location={"latitude": 19.0, "longitude": 72.8},
        available_metrics=[
            MetricContext(metric="temperature", value=26.0, availability="AVAILABLE"),
        ],
        unavailable_metrics=[
            MetricContext(metric="soil_organic_carbon", availability="UNAVAILABLE", unavailability_reason="Upstream downtime"),
            MetricContext(metric="soil_ph", availability="UNAVAILABLE", unavailability_reason="Upstream downtime"),
        ],
        relationships=[],
        overall_interpretation="Sparse site.",
        limitations=["Soil unavailable."],
    )

    recs = generate_recommendations_from_reasoning(reasoning_res)
    soil_rec = next((r for r in recs if r.category == "soil_stewardship"), None)

    assert soil_rec is not None
    assert "Soil Testing" in soil_rec.title
    assert any("laboratory" in lim.lower() for lim in soil_rec.limitations)
    assert soil_rec.confidence_score is None


def test_status_lifecycle_workflow_persistence(db_session):
    """Verifies status transitions: suggested -> in-progress -> implemented -> dismissed."""
    evidence_item = LinkedEvidence(
        document_id="doc-test-1",
        chunk_id="chunk-test-1",
        source="IPCC",
        title="Climate Change and Land",
        organization="IPCC",
        publication_year=2019,
        excerpt="Water management reduces runoff...",
        retrieval_score=0.52,
    )
    relationship = EnvironmentalRelationship(
        relationship_id="rel-water-1",
        relationship_type="climate_land_water_dynamics",
        title="Hydrological Dynamics",
        metrics=["temperature", "rainfall", "land_cover_class"],
        metrics_count=3,
        is_multi_metric=True,
        interpretation="Runoff interaction.",
        evidence_status="supported",
        evidence=[evidence_item],
    )
    reasoning_res = ReasoningResponse(
        location={"latitude": 18.5, "longitude": 73.8},
        available_metrics=[
            MetricContext(metric="temperature", value=25.0, availability="AVAILABLE"),
            MetricContext(metric="rainfall", value=5.0, availability="AVAILABLE"),
            MetricContext(metric="land_cover_class", value="Grassland", availability="AVAILABLE"),
        ],
        unavailable_metrics=[],
        relationships=[relationship],
        overall_interpretation="Grassland site.",
        limitations=[],
    )

    req = RecommendationGenerateRequest(reasoning_response=reasoning_res)
    res = generate_recommendations(req, db_session)
    assert res.total >= 1
    rec_id = res.items[0].id

    # 1. Initial status is suggested
    item = get_recommendation(rec_id, db_session)
    assert item.status == "suggested"

    # 2. Update to in-progress
    updated = update_recommendation_status(rec_id, "in-progress", db_session)
    assert updated.status == "in-progress"

    # 3. Update to implemented
    updated = update_recommendation_status(rec_id, "implemented", db_session)
    assert updated.status == "implemented"

    # 4. Update to dismissed
    updated = update_recommendation_status(rec_id, "dismissed", db_session)
    assert updated.status == "dismissed"

    # 5. Invalid status raises ValueError
    with pytest.raises(ValueError):
        update_recommendation_status(rec_id, "invalid_status", db_session)


def test_recommendation_api_endpoints():
    """Verifies FastAPI /api/recommendations endpoints with camelCase serialization."""
    client = TestClient(app)

    evidence_item = {
        "documentId": "doc-api-1",
        "chunkId": "chunk-api-1",
        "source": "FAO",
        "title": "State of Knowledge of Soil Biodiversity",
        "organization": "FAO",
        "publicationYear": 2020,
        "excerpt": "Agroforestry buffers protect biodiversity.",
        "retrievalScore": 0.60,
        "matchedMetrics": ["temperature", "observed_species_richness"],
    }
    relationship = {
        "relationshipId": "rel-api-1",
        "relationshipType": "climate_land_biodiversity_context",
        "title": "Climate, Land-Cover & Biodiversity Context",
        "metrics": ["temperature", "rainfall", "land_cover_class", "observed_species_richness"],
        "metricsCount": 4,
        "isMultiMetric": True,
        "interpretation": "Agricultural climate-biodiversity interaction.",
        "evidenceStatus": "supported",
        "evidence": [evidence_item],
        "limitations": [],
    }
    reasoning_res = {
        "location": {"latitude": 19.8, "longitude": 74.4},
        "availableMetrics": [
            {"metric": "temperature", "value": 24.8, "unit": "C", "availability": "AVAILABLE"},
            {"metric": "land_cover_class", "value": "Cropland", "availability": "AVAILABLE"},
            {"metric": "observed_species_richness", "value": 120, "availability": "AVAILABLE"},
        ],
        "unavailableMetrics": [
            {"metric": "soil_organic_carbon", "availability": "UNAVAILABLE", "unavailabilityReason": "SoilGrids down"},
        ],
        "relationships": [relationship],
        "overallInterpretation": "Cropland zone.",
        "limitations": [],
    }

    # 1. POST /api/recommendations/generate
    gen_resp = client.post(
        "/api/recommendations/generate",
        json={"reasoningResponse": reasoning_res},
    )
    assert gen_resp.status_code == 200
    gen_data = gen_resp.json()
    assert "items" in gen_data
    assert len(gen_data["items"]) >= 1

    first_rec = gen_data["items"][0]
    rec_id = first_rec["id"]
    assert "title" in first_rec
    assert "confidence" in first_rec
    assert first_rec.get("confidenceScore") is None  # Defensible null

    # 2. GET /api/recommendations
    list_resp = client.get("/api/recommendations")
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert any(r["id"] == rec_id for r in items)

    # 3. GET /api/recommendations/{id}
    detail_resp = client.get(f"/api/recommendations/{rec_id}")
    assert detail_resp.status_code == 200
    assert detail_resp.json()["id"] == rec_id

    # 4. PATCH /api/recommendations/{id}/status
    patch_resp = client.patch(
        f"/api/recommendations/{rec_id}/status",
        json={"status": "in-progress"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "in-progress"
