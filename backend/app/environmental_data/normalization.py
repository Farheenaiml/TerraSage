from __future__ import annotations

from math import isnan
from typing import Any


def normalize_numeric(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "")
        try:
            value = float(cleaned)
        except ValueError:
            return None
    if isinstance(value, (int, float)) and not isnan(value):
        return float(value)
    return None


def normalize_metric_name(metric: str | None) -> str:
    if not metric:
        return ""
    mapping = {
        "temperature": "temperature",
        "rainfall": "rainfall",
        "soil_pH": "soil_pH",
        "soilph": "soil_pH",
        "soil_organic_carbon": "soil_organic_carbon",
        "orgc": "soil_organic_carbon",
        "land_cover_class": "land_cover_class",
        "distinct_species_count": "distinct_species_count",
        "observation_count": "observation_count",
    }
    return mapping.get(metric, metric)


def normalize_unit(unit: str | None) -> str | None:
    if not unit:
        return None
    replacements = {
        "C": "C",
        "degC": "C",
        "°C": "C",
        "mm/month": "mm",
        "mm": "mm",
        "g/kg": "g/kg",
        "ph": "pH",
        "pH": "pH",
    }
    return replacements.get(unit, unit)
