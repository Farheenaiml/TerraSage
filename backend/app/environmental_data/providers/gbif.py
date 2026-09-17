from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from app.environmental_data.providers.base import BaseProvider


class GBIFProvider(BaseProvider):
    provider_name = "GBIF"

    def get_data(self, latitude: float, longitude: float, **options: Any) -> dict[str, Any]:
        radius_km = options.get("radius_km", 10.0)
        url = "https://api.gbif.org/v1/occurrence/search"
        # Use GBIF native faceting to aggregate distinct speciesKey across the entire result set
        params = {
            "geoDistance": f"{latitude},{longitude},{radius_km}km",
            "facet": "speciesKey",
            "facetLimit": 10000,
            "limit": 0,
        }
        try:
            response = httpx.get(url, params=params, timeout=30)
        except httpx.HTTPError as exc:
            return {
                "provider": self.provider_name,
                "status": "ERROR",
                "message": f"GBIF request failed: {exc}",
                "observations": [],
            }

        if response.status_code != 200:
            return {
                "provider": self.provider_name,
                "status": "ERROR",
                "message": f"GBIF returned {response.status_code}",
                "observations": [],
            }

        data = response.json()
        observations = parse_gbif_response(data, latitude=latitude, longitude=longitude, radius_km=radius_km)
        return {
            "provider": self.provider_name,
            "status": "AVAILABLE",
            "observations": observations,
            "raw": {"count": data.get("count"), "facets_returned": len(data.get("facets", []))},
        }


def parse_gbif_response(
    payload: dict[str, Any],
    latitude: float | None = None,
    longitude: float | None = None,
    radius_km: float = 10.0,
) -> list[dict[str, Any]]:
    total_in_radius = payload.get("count", 0)

    # 1. Check for complete faceted speciesKey aggregation from GBIF Solr
    unique_species: set[int | str] = set()
    facets = payload.get("facets", [])
    for f in facets:
        field_name = (f.get("field") or "").upper()
        if field_name in {"SPECIES_KEY", "SPECIESKEY"}:
            for item in f.get("counts", []):
                val = item.get("name")
                if val:
                    try:
                        unique_species.add(int(val))
                    except ValueError:
                        unique_species.add(val)

    # 2. Fallback to result list (e.g. mock test payloads or paginated results)
    if not unique_species and "results" in payload:
        results = payload.get("results", [])
        if total_in_radius == 0:
            total_in_radius = len(results)
        for item in results:
            sp_key = item.get("speciesKey")
            if sp_key is not None:
                unique_species.add(sp_key)

    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    note = (
        "Observed species richness from GBIF occurrence records; "
        "affected by observation/sampling effort."
    )

    return [
        {
            "metric": "observation_count",
            "value": total_in_radius,
            "unit": "records",
            "source": "GBIF",
            "latitude": latitude,
            "longitude": longitude,
            "retrieval_timestamp": timestamp,
            "metadata": {
                "observation_basis": "GBIF occurrence records",
                "radius_km": radius_km,
                "total_records_in_radius": total_in_radius,
            },
        },
        {
            "metric": "distinct_species_count",
            "value": len(unique_species),
            "unit": "species",
            "source": "GBIF",
            "latitude": latitude,
            "longitude": longitude,
            "retrieval_timestamp": timestamp,
            "metadata": {
                "indicator_name": "Observed species richness from GBIF occurrence records",
                "observation_basis": "GBIF occurrence records",
                "radius_km": radius_km,
                "note": note,
                "aggregation_method": "full_dataset_speciesKey_facet" if facets else "results_deduplication",
            },
        },
    ]
