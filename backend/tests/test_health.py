from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from app.core.database import get_db
from app.main import app


def test_health_endpoint_reports_service_status():
    response = TestClient(app).get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] in {"ok", "degraded"}


def test_health_reports_unavailable_database():
    with patch("app.main.engine") as engine:
        engine.connect.side_effect = OperationalError(
            "SELECT 1", {}, Exception("database unavailable")
        )

        response = TestClient(app).get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "degraded", "database": "unavailable"}


def test_database_route_errors_return_service_unavailable():
    previous_overrides = app.dependency_overrides.copy()
    app.dependency_overrides[get_db] = lambda: None

    try:
        with patch(
            "app.api.routes.conversations.conv_service.list_conversations",
            side_effect=OperationalError(
                "SELECT conversations", {}, Exception("database unavailable")
            ),
        ):
            response = TestClient(app, raise_server_exceptions=False).get(
                "/api/conversations"
            )
    finally:
        app.dependency_overrides.clear()
        app.dependency_overrides.update(previous_overrides)

    assert response.status_code == 503
    assert "DATABASE_URL" in response.json()["detail"]
