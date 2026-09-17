"""
Chunk 7A Focused Test Suite: Human-Impact Data Layer
Tests:
1. Air Quality provider live and structured output
2. Air Quality observation schema, units, and timestamps
3. Hansen Global Forest Change honest unconfigured state (UNAVAILABLE + reason)
4. Hansen Global Forest Change parsing when GFW payload is provided
5. Environmental service provider loop integration
6. API endpoint exposure of human-impact data in environmental profile
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.environmental_data.providers.air_quality import AirQualityProvider
from app.environmental_data.providers.hansen_forest_change import HansenForestChangeProvider
from app.environmental_data.service import collect_environmental_data


@pytest.fixture
def client():
    return TestClient(app)


def test_air_quality_provider_output():
    """Verifies AirQualityProvider produces structured PM2.5 observations without hallucinated values."""
    provider = AirQualityProvider()
    data = provider.get_data(latitude=19.9975, longitude=73.7898)
    assert "status" in data
    assert data["status"] in {"AVAILABLE", "UNAVAILABLE"}

    if data["status"] == "AVAILABLE":
        obs = data["observations"]
        assert len(obs) > 0
        pm25_obs = next((o for o in obs if o["metric"] == "pm2_5"), None)
        assert pm25_obs is not None
        assert isinstance(pm25_obs["value"], (int, float))
        assert pm25_obs["value"] >= 0
        assert pm25_obs["unit"] == "ug/m3"
        assert "Copernicus" in pm25_obs["source"] or "OpenAQ" in pm25_obs["source"]
        assert pm25_obs["period_start"] is not None
        assert "metadata" in pm25_obs


def test_hansen_forest_change_honest_unconfigured_state():
    """Verifies Hansen provider honestly reports UNAVAILABLE when API key is unconfigured."""
    provider = HansenForestChangeProvider()
    data = provider.get_data(latitude=19.9975, longitude=73.7898)

    assert data["status"] == "UNAVAILABLE"
    assert "requires a valid API key" in data["message"] or "GFW_API_KEY" in data["message"]
    assert len(data["observations"]) == 0
    # Does NOT use static WorldCover as a fake deforestation rate
    assert "WorldCover" not in data.get("raw", {}).get("notice", "") or "not used as a fake deforestation rate" in data.get("raw", {}).get("notice", "")


def test_hansen_forest_change_simulated_payload_parsing(monkeypatch):
    """Verifies Hansen provider parses valid GFW response into structured annual tree cover loss."""
    provider = HansenForestChangeProvider()

    class MockResponse:
        status_code = 200
        def json(self):
            return {
                "data": [
                    {"umd_tree_cover_loss__year": 2023, "loss_area_ha": 452.1},
                    {"umd_tree_cover_loss__year": 2022, "loss_area_ha": 389.4},
                ]
            }

    import httpx
    monkeypatch.setenv("GFW_API_KEY", "test_mock_gfw_key")
    monkeypatch.setattr(httpx, "get", lambda *args, **kwargs: MockResponse())

    data = provider.get_data(latitude=-3.4653, longitude=-62.2159)
    assert data["status"] == "AVAILABLE"
    assert len(data["observations"]) == 2
    obs0 = data["observations"][0]
    assert obs0["metric"] == "annual_tree_cover_loss"
    assert obs0["value"] == 452.1
    assert obs0["unit"] == "ha"
    assert obs0["period_start"] == "2023-01-01"
    assert obs0["source"] == "Hansen/UMD Global Forest Change v1.11"


def test_environmental_service_integrates_human_impact():
    """Verifies collect_environmental_data incorporates human impact in provider_status and profile."""
    res = collect_environmental_data(latitude=19.9975, longitude=73.7898)
    assert "air_quality" in res["provider_status"]
    assert "hansen_forest_change" in res["provider_status"]

    profile = res["profile"]
    assert "human_impact" in profile
    # If air quality succeeded, human_impact contains pm2_5
    if res["provider_status"]["air_quality"]["status"] == "AVAILABLE":
        assert "pm2_5" in profile["human_impact"]
        assert profile["human_impact"]["pm2_5_unit"] == "ug/m3"


def test_environment_profile_api_endpoint_exposes_human_impact(client):
    """Verifies GET /api/environment/profile endpoint returns human_impact section."""
    response = client.get("/api/environment/profile?latitude=19.9975&longitude=73.7898")
    assert response.status_code == 200
    data = response.json()
    assert "human_impact" in data or "humanImpact" in data
