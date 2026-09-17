from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

import httpx

from app.environmental_data.providers.base import BaseProvider

WORLD_COVER_CLASSES = {
    10: "Tree cover",
    20: "Shrubland",
    30: "Grassland",
    40: "Cropland",
    50: "Built-up",
    60: "Bare / sparse vegetation",
    70: "Snow and ice",
    80: "Permanent water bodies",
    90: "Herbaceous wetland",
    95: "Mangroves",
    100: "Moss and lichen",
}


def get_worldcover_tile_id(latitude: float, longitude: float) -> str:
    lat_block = int(math.floor(latitude / 3.0) * 3)
    lat_hemi = "N" if lat_block >= 0 else "S"
    lat_str = f"{lat_hemi}{abs(lat_block):02d}"

    lon_block = int(math.floor(longitude / 3.0) * 3)
    lon_hemi = "E" if lon_block >= 0 else "W"
    lon_str = f"{lon_hemi}{abs(lon_block):03d}"

    return f"ESA_WorldCover_10m_2021_v200_{lat_str}{lon_str}"


def classify_worldcover_response(
    payload: dict[str, Any],
    latitude: float | None = None,
    longitude: float | None = None,
    tile_id: str | None = None,
    source_url: str | None = None,
) -> dict[str, Any]:
    class_code = None
    if "values" in payload and payload["values"]:
        class_code = int(payload["values"][0])
    elif "value" in payload:
        class_code = int(payload["value"])

    class_name = payload.get("attributes", {}).get("LC_CLASS") or WORLD_COVER_CLASSES.get(class_code, f"Class {class_code}")

    lat = latitude
    if lat is None and isinstance(payload.get("location"), dict):
        lat = payload["location"].get("y")

    lon = longitude
    if lon is None and isinstance(payload.get("location"), dict):
        lon = payload["location"].get("x")

    return {
        "metric": "land_cover_class",
        "value": class_name,
        "unit": "class",
        "source": "ESA WorldCover 2021",
        "latitude": lat,
        "longitude": lon,
        "retrieval_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "metadata": {
            "land_cover_class_code": class_code,
            "land_cover_class_name": class_name,
            "dataset": "ESA WorldCover",
            "version": "2021 v200",
            "tile_id": tile_id,
            "source_api": source_url,
        },
        "class_code": class_code,
        "class_name": class_name,
    }


class WorldCoverProvider(BaseProvider):
    provider_name = "ESA WorldCover 2021"

    def get_data(self, latitude: float, longitude: float, **options: Any) -> dict[str, Any]:
        tile_id = get_worldcover_tile_id(latitude, longitude)
        point_url = (
            f"https://planetarycomputer.microsoft.com/api/data/v1/item/point/{longitude},{latitude}"
            f"?collection=esa-worldcover&item={tile_id}&assets=map"
        )
        
        try:
            response = httpx.get(point_url, timeout=20)
        except httpx.HTTPError as exc:
            return {
                "provider": self.provider_name,
                "status": "ERROR",
                "message": f"WorldCover request failed: {exc}",
                "observations": [],
            }

        if response.status_code != 200:
            return {
                "provider": self.provider_name,
                "status": "UNAVAILABLE",
                "message": f"WorldCover tile query returned HTTP {response.status_code} for tile {tile_id}",
                "observations": [],
            }

        data = response.json()
        values = data.get("values", [])
        if not values:
            return {
                "provider": self.provider_name,
                "status": "UNAVAILABLE",
                "message": f"No raster values returned for coordinates ({latitude}, {longitude})",
                "observations": [],
            }

        observation = classify_worldcover_response(
            data,
            latitude=latitude,
            longitude=longitude,
            tile_id=tile_id,
            source_url=point_url,
        )

        return {
            "provider": self.provider_name,
            "status": "AVAILABLE",
            "observations": [observation],
            "raw": data,
        }
