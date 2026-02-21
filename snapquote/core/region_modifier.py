from __future__ import annotations


def resolve_region_multiplier(industry: dict, region: str) -> float:
    return float(industry.get("region_modifiers", {}).get(region, 1.0))


def resolve_urgency_multiplier(industry: dict, urgency: str) -> float:
    return float(industry.get("urgency_modifiers", {}).get(urgency, 1.0))
