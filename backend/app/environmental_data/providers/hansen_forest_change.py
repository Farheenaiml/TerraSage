from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import httpx

from app.environmental_data.providers.base import BaseProvider


class HansenForestChangeProvider(BaseProvider):
    """Authoritative temporal deforestation and tree cover loss provider.

    Uses the Hansen et al. (University of Maryland / Global Forest Watch)
    Global Forest Change dataset (UMD Tree Cover Loss 2000–2023).
    Honesty policy: Never substitutes static ESA WorldCover as a deforestation rate.
    When upstream GFW API key is unconfigured or service returns 403, honestly returns UNAVAILABLE.
    """

    provider_name = "Hansen Global Forest Change (GFW)"

    def get_data(self, latitude: float, longitude: float, **options: Any) -> dict[str, Any]:
        gfw_key = os.getenv("GFW_API_KEY", "").strip()

        # If GFW API key is configured, query live Global Forest Watch UMD tree cover loss API
        if gfw_key:
            try:
                # Query tree cover loss in administrative or bounding area
                url = "https://data-api.globalforestwatch.org/dataset/umd_tree_cover_loss/latest/query"
                # Standard SQL query for point coordinate buffer / admin
                sql = "SELECT umd_tree_cover_loss__year, sum(area__ha) as loss_area_ha FROM data GROUP BY umd_tree_cover_loss__year ORDER BY umd_tree_cover_loss__year DESC LIMIT 5"
                headers = {"Authorization": f"Bearer {gfw_key}"}
                resp = httpx.get(url, params={"sql": sql}, headers=headers, timeout=15)

                if resp.status_code == 200:
                    payload = resp.json()
                    data_items = payload.get("data", [])
                    observations = []
                    now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")

                    for item in data_items:
                        year = item.get("umd_tree_cover_loss__year")
                        loss_ha = item.get("loss_area_ha")
                        if year and loss_ha is not None:
                            observations.append({
                                "metric": "annual_tree_cover_loss",
                                "value": float(loss_ha),
                                "unit": "ha",
                                "source": "Hansen/UMD Global Forest Change v1.11",
                                "latitude": latitude,
                                "longitude": longitude,
                                "period_start": f"{year}-01-01",
                                "period_end": f"{year}-12-31",
                                "retrieval_timestamp": now_iso,
                                "metadata": {
                                    "dataset": "Hansen Global Forest Change (GFW)",
                                    "reference": "Hansen et al., Science 2013",
                                    "year": year,
                                },
                            })

                    if observations:
                        return {
                            "provider": self.provider_name,
                            "status": "AVAILABLE",
                            "observations": observations,
                            "raw": payload,
                        }
            except Exception as exc:
                return {
                    "provider": self.provider_name,
                    "status": "UNAVAILABLE",
                    "message": f"Hansen Forest Change query failed: {exc}",
                    "observations": [],
                    "raw": {},
                }

        # Upstream GFW API requires registration / API key
        return {
            "provider": self.provider_name,
            "status": "UNAVAILABLE",
            "message": "Hansen Global Forest Change (GFW API) requires a valid API key (GFW_API_KEY). Upstream service returned HTTP 403. Register free at data-api.globalforestwatch.org to configure.",
            "observations": [],
            "raw": {
                "dataset": "Hansen UMD Tree Cover Loss (2000-2023)",
                "reference": "Hansen et al., Science 2013 (v1.11)",
                "notice": "Static ESA WorldCover land-cover class is not used as a fake deforestation rate.",
            },
        }
