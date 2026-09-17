from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import httpx

from app.environmental_data.normalization import normalize_numeric
from app.environmental_data.providers.base import BaseProvider

SOILGRIDS_PROPERTIES = {
    "phhox": {
        "metric": "soil_pH",
        "raw_unit": "pH*10",
        "normalized_unit": "pH",
        "conversion_factor": 0.1,
    },
    "phihox": {
        "metric": "soil_pH",
        "raw_unit": "pH",
        "normalized_unit": "pH",
        "conversion_factor": 1.0,
    },
    "soc": {
        "metric": "soil_organic_carbon",
        "raw_unit": "dg/kg",
        "normalized_unit": "g/kg",
        "conversion_factor": 0.1,
    },
    "orcdrc": {
        "metric": "soil_organic_carbon",
        "raw_unit": "g/kg",
        "normalized_unit": "g/kg",
        "conversion_factor": 1.0,
    },
}


class SoilGridsProvider(BaseProvider):
    provider_name = "SoilGrids"

    def get_data(self, latitude: float, longitude: float, **options: Any) -> dict[str, Any]:
        depth = options.get("depth", "0-5cm")
        rest_url = f"https://rest.isric.org/soilgrids/v2.0/properties/query?lon={longitude}&lat={latitude}&property=phhox&property=soc&depth={depth}"
        
        try:
            response = httpx.get(rest_url, timeout=20)
            if response.status_code == 200:
                payload = response.json()
                observations = parse_soilgrids_response(payload, latitude=latitude, longitude=longitude, depth=depth)
                if observations:
                    return {
                        "provider": self.provider_name,
                        "status": "AVAILABLE",
                        "observations": observations,
                        "raw": payload,
                    }
        except Exception:
            pass

        # If REST endpoint is unavailable/paused (e.g. 500/503), report honestly
        return {
            "provider": self.provider_name,
            "status": "UNAVAILABLE",
            "message": "Official SoilGrids REST and WCS services are currently unavailable upstream.",
            "observations": [],
            "raw": {},
        }


def parse_soilgrids_response(
    payload: dict[str, Any],
    latitude: float | None = None,
    longitude: float | None = None,
    depth: str = "0-5cm",
    metric: str | None = None,
    layer_name: str | None = None,
) -> list[dict[str, Any]]:
    properties = payload.get("properties", {})
    layers = properties.get("layers", [])
    results: list[dict[str, Any]] = []

    for layer in layers:
        prop_name = layer.get("name", "").lower()
        prop_info = SOILGRIDS_PROPERTIES.get(prop_name)
        if not prop_info:
            continue

        for d_info in layer.get("depths", []):
            depth_label = d_info.get("name") or depth
            values = d_info.get("values", {})
            raw_mean = normalize_numeric(values.get("mean"))
            if raw_mean is None:
                continue

            # Auto-detect scaling: if pH is > 14, it is scaled by 10 (e.g. 64 -> 6.4)
            factor = prop_info["conversion_factor"]
            if prop_info["metric"] == "soil_pH" and raw_mean > 14:
                factor = 0.1
            elif prop_info["metric"] == "soil_pH" and raw_mean <= 14:
                factor = 1.0

            norm_val = round(raw_mean * factor, 2)
            uncertainty = values.get("uncertainty")

            results.append({
                "metric": prop_info["metric"],
                "value": norm_val,
                "unit": prop_info["normalized_unit"],
                "source": "ISRIC SoilGrids",
                "depth_or_layer": depth_label,
                "latitude": latitude or payload.get("lat"),
                "longitude": longitude or payload.get("lon"),
                "retrieval_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "metadata": {
                    "soilgrids_property": prop_name,
                    "original_value": raw_mean,
                    "original_unit": prop_info["raw_unit"],
                    "normalized_value": norm_val,
                    "normalized_unit": prop_info["normalized_unit"],
                    "conversion_factor": factor,
                    "uncertainty": uncertainty,
                    "depth_interval": depth_label,
                },
            })

    return results
