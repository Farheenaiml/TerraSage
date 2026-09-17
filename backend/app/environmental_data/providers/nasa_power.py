from __future__ import annotations

import calendar
from datetime import datetime, timezone
from typing import Any

import httpx

from app.environmental_data.normalization import normalize_numeric
from app.environmental_data.providers.base import BaseProvider


class NASAPOWERProvider(BaseProvider):
    provider_name = "NASA POWER"

    def get_data(self, latitude: float, longitude: float, **options: Any) -> dict[str, Any]:
        params = options.get("parameters") or ["T2M", "PRECTOTCORR"]
        current_year = datetime.now(timezone.utc).year
        default_year = current_year - 1 if current_year > 2023 else 2023
        start_raw = options.get("start_date") or str(default_year)
        end_raw = options.get("end_date") or str(default_year)
        start_year = str(start_raw)[:4]
        end_year = str(end_raw)[:4]

        url = "https://power.larc.nasa.gov/api/temporal/monthly/point"
        payload = {
            "latitude": latitude,
            "longitude": longitude,
            "parameters": ",".join(params),
            "community": "RE",
            "start": start_year,
            "end": end_year,
            "format": "JSON",
        }
        try:
            response = httpx.get(url, params=payload, timeout=30)
        except httpx.HTTPError as exc:
            return {
                "provider": self.provider_name,
                "status": "ERROR",
                "message": f"NASA POWER request failed: {exc}",
                "observations": [],
            }

        if response.status_code != 200:
            return {
                "provider": self.provider_name,
                "status": "ERROR",
                "message": f"NASA POWER returned {response.status_code}",
                "observations": [],
            }

        data = response.json()
        observations = parse_nasa_power_response(data, latitude=latitude, longitude=longitude, url=url)
        return {
            "provider": self.provider_name,
            "status": "AVAILABLE" if observations else "UNAVAILABLE",
            "observations": observations,
            "raw": data,
        }


def parse_nasa_power_response(
    payload: dict[str, Any],
    latitude: float | None = None,
    longitude: float | None = None,
    url: str = "https://power.larc.nasa.gov/api/temporal/monthly/point",
) -> list[dict[str, Any]]:
    properties = payload.get("properties", {})
    params = properties.get("parameter", {})
    observations: list[dict[str, Any]] = []

    # Process PRECTOTCORR monthly values to compute monthly & annual accumulations
    raw_precip = params.get("PRECTOTCORR", {})

    for key, values in params.items():
        norm = key.strip().upper()
        if norm == "T2M":
            metric = "temperature"
            native_unit = "C"
        elif norm == "PRECTOTCORR":
            metric = "rainfall"
            native_unit = "mm/day"
        else:
            metric = norm.lower()
            native_unit = "unknown"

        for period, raw_val in sorted(values.items()):
            numeric = normalize_numeric(raw_val)
            if numeric is None or numeric == -999.0:
                continue

            is_annual = len(period) >= 6 and period[4:6] == "13"
            year = int(period[:4])

            if is_annual:
                period_start = f"{year}-01-01"
                period_end = f"{year}-12-31"
                num_days = 366 if calendar.isleap(year) else 365
                temporal_meaning = "annual_mean_daily_precipitation_rate" if metric == "rainfall" else "annual_mean_temperature"
            else:
                month = int(period[4:6])
                _, num_days = calendar.monthrange(year, month)
                period_start = f"{year}-{month:02d}-01"
                period_end = f"{year}-{month:02d}-{num_days:02d}"
                temporal_meaning = "monthly_mean_daily_precipitation_rate" if metric == "rainfall" else "monthly_mean_temperature"

            metadata: dict[str, Any] = {
                "provider": "nasa_power",
                "original_parameter": norm,
                "raw_period": period,
                "is_annual_average": is_annual,
                "temporal_meaning": temporal_meaning,
                "source_url": url,
                "days_in_period": num_days,
            }

            if metric == "rainfall":
                metadata["rainfall_representation"] = "mean_daily_precipitation"
                metadata["daily_rate_unit"] = "mm/day"
                accumulated_mm = round(numeric * num_days, 2)
                metadata["accumulated_precipitation_mm"] = accumulated_mm
            elif metric == "temperature":
                metadata["temperature_representation"] = "mean_2m_temperature"
                metadata["temperature_unit"] = "C"

            observations.append({
                "metric": metric,
                "value": numeric,
                "unit": native_unit,
                "source": "NASA POWER",
                "latitude": latitude,
                "longitude": longitude,
                "period_start": period_start,
                "period_end": period_end,
                "retrieval_timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "metadata": metadata,
            })

    return observations
