from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

import httpx

from app.environmental_data.providers.base import BaseProvider


class AirQualityProvider(BaseProvider):
    """Authoritative air quality and pollution provider.

    Supports OpenAQ v3 when OPENAQ_API_KEY is configured.
    Uses Copernicus CAMS (Atmosphere Monitoring Service via Open-Meteo) as the open authoritative source.
    """

    provider_name = "Air Quality (OpenAQ / Copernicus CAMS)"

    def get_data(self, latitude: float, longitude: float, **options: Any) -> dict[str, Any]:
        openaq_key = os.getenv("OPENAQ_API_KEY", "").strip()

        # 1. Attempt OpenAQ v3 if API key is provided
        if openaq_key:
            try:
                openaq_url = f"https://api.openaq.org/v3/locations?coordinates={latitude},{longitude}&radius=25000"
                headers = {"X-API-Key": openaq_key}
                resp = httpx.get(openaq_url, headers=headers, timeout=12)
                if resp.status_code == 200:
                    payload = resp.json()
                    observations = self._parse_openaq_v3(payload, latitude, longitude)
                    if observations:
                        return {
                            "provider": "OpenAQ v3",
                            "status": "AVAILABLE",
                            "observations": observations,
                            "raw": payload,
                        }
            except Exception:
                pass  # Fallback to Copernicus CAMS

        # 2. Query open authoritative Copernicus CAMS Air Quality Service
        cams_url = (
            f"https://air-quality-api.open-meteo.com/v1/air-quality?"
            f"latitude={latitude}&longitude={longitude}&current=pm2_5,pm10,european_aqi,us_aqi"
        )
        try:
            resp = httpx.get(cams_url, timeout=15)
            if resp.status_code == 200:
                payload = resp.json()
                current = payload.get("current", {})
                time_str = current.get("time")
                pm25 = current.get("pm2_5")
                pm10 = current.get("pm10")
                aqi = current.get("us_aqi")

                observations = []
                now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")

                if pm25 is not None:
                    observations.append({
                        "metric": "pm2_5",
                        "value": float(pm25),
                        "unit": "ug/m3",
                        "source": "Copernicus CAMS / Open-Meteo",
                        "latitude": latitude,
                        "longitude": longitude,
                        "period_start": time_str or now_iso,
                        "period_end": time_str or now_iso,
                        "retrieval_timestamp": now_iso,
                        "metadata": {
                            "parameter": "Fine Particulate Matter (PM2.5)",
                            "model": "Copernicus Atmosphere Monitoring Service (CAMS)",
                            "european_aqi": current.get("european_aqi"),
                            "us_aqi": aqi,
                        },
                    })

                if pm10 is not None:
                    observations.append({
                        "metric": "pm10",
                        "value": float(pm10),
                        "unit": "ug/m3",
                        "source": "Copernicus CAMS / Open-Meteo",
                        "latitude": latitude,
                        "longitude": longitude,
                        "period_start": time_str or now_iso,
                        "period_end": time_str or now_iso,
                        "retrieval_timestamp": now_iso,
                        "metadata": {
                            "parameter": "Coarse Particulate Matter (PM10)",
                            "model": "Copernicus Atmosphere Monitoring Service (CAMS)",
                        },
                    })

                if aqi is not None:
                    observations.append({
                        "metric": "air_quality_index",
                        "value": int(aqi),
                        "unit": "AQI",
                        "source": "Copernicus CAMS / Open-Meteo",
                        "latitude": latitude,
                        "longitude": longitude,
                        "period_start": time_str or now_iso,
                        "period_end": time_str or now_iso,
                        "retrieval_timestamp": now_iso,
                        "metadata": {
                            "standard": "US EPA Air Quality Index",
                        },
                    })

                return {
                    "provider": "Copernicus CAMS / Open-Meteo",
                    "status": "AVAILABLE",
                    "observations": observations,
                    "raw": payload,
                }

            return {
                "provider": self.provider_name,
                "status": "UNAVAILABLE",
                "message": f"Copernicus CAMS returned HTTP {resp.status_code}",
                "observations": [],
                "raw": {},
            }

        except Exception as exc:
            return {
                "provider": self.provider_name,
                "status": "UNAVAILABLE",
                "message": f"Air quality query failed: {exc}",
                "observations": [],
                "raw": {},
            }

    def _parse_openaq_v3(self, payload: dict[str, Any], lat: float, lon: float) -> list[dict[str, Any]]:
        results = payload.get("results", [])
        observations = []
        now_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")
        for loc in results:
            sensors = loc.get("sensors", [])
            for s in sensors:
                param = (s.get("parameter") or {}).get("name", "").lower()
                if param in {"pm25", "pm2.5", "pm2_5"}:
                    latest = s.get("latest") or {}
                    val = latest.get("value")
                    if val is not None:
                        observations.append({
                            "metric": "pm2_5",
                            "value": float(val),
                            "unit": "ug/m3",
                            "source": f"OpenAQ v3 ({loc.get('name', 'Station')})",
                            "latitude": lat,
                            "longitude": lon,
                            "period_start": latest.get("datetime"),
                            "period_end": latest.get("datetime"),
                            "retrieval_timestamp": now_iso,
                            "metadata": {"sensor_id": s.get("id"), "location_id": loc.get("id")},
                        })
                        return observations  # Return nearest reading
        return observations
