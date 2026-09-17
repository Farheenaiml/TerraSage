from fastapi.testclient import TestClient

from app.main import app


def test_knowledge_search_validates_short_queries():
    response = TestClient(app).post("/api/knowledge/search", json={"query": "no"})
    assert response.status_code == 422


def test_sources_endpoint_returns_registered_sources():
    response = TestClient(app).get("/api/knowledge/sources")
    assert response.status_code == 200
    assert isinstance(response.json(), list)