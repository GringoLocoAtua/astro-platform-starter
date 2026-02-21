from __future__ import annotations

from ai.image_tagging import analyze_image
from core.client_vault import save_quote
from core.industry_registry import IndustryRegistry
from core.pricing_engine import calculate_quote
from core.validation import ValidationError, normalize_request


class _OverrideRegistry:
    def __init__(self, default_registry: IndustryRegistry, override: dict | None) -> None:
        self.default_registry = default_registry
        self.override = override

    def get_industry(self, industry_id: str) -> dict:
        if self.override and self.override.get("id") == industry_id:
            return self.override
        return self.default_registry.get_industry(industry_id)


def analyze_images(image_paths: list[str]) -> list[str]:
    tags: list[str] = []
    for image_path in image_paths or []:
        try:
            tags.extend(analyze_image(image_path))
        except Exception:
            continue
    return tags


def build_quote(request: dict, confirmed_tags: list[str] | None = None, industry_override: dict | None = None) -> dict:
    registry = IndustryRegistry()
    normalized = normalize_request(request)

    image_tags = confirmed_tags if confirmed_tags is not None else analyze_images(normalized.image_paths)

    try:
        quote = calculate_quote(normalized, _OverrideRegistry(registry, industry_override), image_tags)
    except (ValidationError, KeyError, ValueError) as exc:
        return {
            "error": str(exc),
            "quote_id": "",
            "breakdown": [],
            "assumptions": ["Validation failed"],
        }

    if normalized.client_name:
        save_quote(normalized.client_name, quote)

    return quote
