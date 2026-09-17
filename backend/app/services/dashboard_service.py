from app.schemas.environment import DashboardResponse
from app.services.environment_service import field_status


def build_dashboard(profile) -> DashboardResponse:
    available = profile.available_fields if profile else []
    missing = profile.missing_fields if profile else field_status(None)[1]
    return DashboardResponse(
        profile=profile,
        available_fields=available,
        missing_fields=missing,
        recent_analyses=[],
        recommendations=[],
        evidence_summary={"total": 0, "recentCount": 0, "byType": {}},
    )
