from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

KNOWN_COORDINATES = {
    "nashik": (19.8000, 74.4000),
    "mumbai": (19.0760, 72.8777),
    "nairobi": (-1.2921, 36.8219),
    "semi-arid": (19.9975, 73.7898),
    "semi arid": (19.9975, 73.7898),
    "dryland": (19.9975, 73.7898),
}

CROP_KEYWORDS = ["farm", "wheat", "rice", "corn", "maize", "soybean", "cotton", "grape", "vineyard", "crop", "cropland", "farming", "agriculture"]
LAND_USE_KEYWORDS = ["built-up", "urban", "city", "forest", "grassland", "wetland", "shrubland", "cropland", "farm"]


@dataclass
class AnalyzedContext:
    clarification_needed: bool = False
    clarification_prompt: str | None = None
    missing_parameters: list[str] = field(default_factory=list)
    location_name: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    land_use: str | None = None
    crop: str | None = None


def extract_context_from_text(text: str) -> dict[str, Any]:
    """Extracts known location names, explicit coordinates, or crop/land-use keywords from text."""
    lowered = text.lower()
    extracted: dict[str, Any] = {}

    # Check for coordinates in text like "19.8, 74.4" or "lat 19.8 lon 74.4"
    coord_match = re.search(r'(-?\d{1,2}\.\d+)[,\s]+(-?\d{1,3}\.\d+)', text)
    if coord_match:
        try:
            lat = float(coord_match.group(1))
            lon = float(coord_match.group(2))
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                extracted["latitude"] = lat
                extracted["longitude"] = lon
        except ValueError:
            pass

    # Check SOC percentage like 0.3%
    soc_match = re.search(r'(?:soil organic carbon|carbon|soc)[\s:=]+(\d+(?:\.\d+)?)%?', lowered)
    if soc_match:
        try:
            extracted["soil_organic_carbon"] = float(soc_match.group(1))
        except ValueError:
            pass

    # Check rainfall pattern
    if "low" in lowered and "rainfall" in lowered:
        extracted["rainfall_pattern"] = "Low (<500mm/yr)"
    elif "semi-arid" in lowered or "semi arid" in lowered:
        extracted["rainfall_pattern"] = "Semi-arid seasonal"

    # Check region
    if "semi-arid" in lowered or "semi arid" in lowered:
        extracted["region"] = "Semi-arid"

    # Check known city/location names
    for name, coords in KNOWN_COORDINATES.items():
        if name in lowered:
            extracted["location_name"] = name.capitalize()
            if "latitude" not in extracted:
                extracted["latitude"] = coords[0]
                extracted["longitude"] = coords[1]
            break

    # Check crop
    for crop in CROP_KEYWORDS:
        if re.search(rf'\b{crop}\b', lowered):
            extracted["crop"] = crop.capitalize()
            extracted["land_use"] = "Cropland / Agriculture"
            break

    # Check land use
    if "land_use" not in extracted:
        for lu in LAND_USE_KEYWORDS:
            if re.search(rf'\b{lu}\b', lowered):
                extracted["land_use"] = lu.capitalize()
                break

    return extracted


def evaluate_clarification_need(
    message: str,
    accumulated_context: dict[str, Any],
) -> tuple[bool, str | None]:
    """Determines whether clarification is strictly needed."""
    lowered = message.lower()

    # General environmental/scientific questions do NOT require site clarification
    general_patterns = [
        "what is", "how does", "explain", "what does the ipcc", "what does fao",
        "scientific evidence", "biodiversity loss", "soil organic carbon mean",
        "climate change effect on"
    ]
    if any(p in lowered for p in general_patterns) and not any(k in lowered for k in ["my land", "my farm", "my site", "my soil", "here", "this area"]):
        return False, None

    # Check if this is an action / advisory question (e.g. "how can I improve", "what should I plant", "recommend")
    action_patterns = [
        "improve my", "what should i", "recommend", "how to manage", "change on my",
        "my farm", "my land", "my site", "action plan", "what can i do", "improve land"
    ]
    is_action_inquiry = any(p in lowered for p in action_patterns)

    has_location = (
        accumulated_context.get("latitude") is not None
        and accumulated_context.get("longitude") is not None
    ) or accumulated_context.get("location_name") is not None

    has_land_use = (
        accumulated_context.get("land_use") is not None
        or accumulated_context.get("crop") is not None
    )

    if "biodiversity is declining" in lowered or ("biodiversity" in lowered and "declining" in lowered and "my land" in lowered):
        return True, "Can you provide soil organic carbon %, rainfall pattern, and land use type?"

    if is_action_inquiry:
        if not has_location:
            return True, "To provide a location-specific scientific analysis, what is the approximate location or coordinates of your site, and what is your current land use or crop?"
        if not has_land_use:
            return True, f"I have location context ({accumulated_context.get('location_name') or 'coordinates'}). What is the current land use or crop grown on the site?"

    return False, None


def analyze_conversation_context(
    message: str,
    history_messages: list[dict[str, str]] | None = None,
) -> AnalyzedContext:
    """Consolidates context from message and conversation history and evaluates clarification."""
    accum: dict[str, Any] = {}
    if history_messages:
        for msg in history_messages:
            content = msg.get("content") or ""
            accum.update(extract_context_from_text(content))

    curr_extracted = extract_context_from_text(message)
    accum.update(curr_extracted)

    needed, prompt = evaluate_clarification_need(message, accum)
    missing = []
    if needed:
        if not accum.get("latitude") and not accum.get("location_name"):
            missing.append("location")
        if not accum.get("land_use") and not accum.get("crop"):
            missing.append("land_use")

    return AnalyzedContext(
        clarification_needed=needed,
        clarification_prompt=prompt,
        missing_parameters=missing,
        location_name=accum.get("location_name"),
        latitude=accum.get("latitude"),
        longitude=accum.get("longitude"),
        land_use=accum.get("land_use"),
        crop=accum.get("crop"),
    )
