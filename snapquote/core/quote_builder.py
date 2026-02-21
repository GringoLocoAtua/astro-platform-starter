from __future__ import annotations

from core.client_vault import save_quote
from core.industry_registry import IndustryRegistry
from core.pricing_engine import calculate_quote
from core.validation import ValidationError, normalize_request
from ai.image_tagging import analyze_image


def build_quote(request: dict) -> dict:
    registry = IndustryRegistry()
    normalized = normalize_request(request)

    image_tags: list[str] = []
    for image_path in normalized.image_paths:
        image_tags.extend(analyze_image(image_path))

    try:
        quote = calculate_quote(normalized, registry, image_tags)
    except (ValidationError, KeyError) as exc:
        return {
            "error": str(exc),
            "quote_id": "",
            "breakdown": [],
            "assumptions": ["Validation failed"],
        }

    if normalized.client_name:
        save_quote(normalized.client_name, quote)

    return quote
