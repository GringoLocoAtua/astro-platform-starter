from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from core.constants import SUPPORTED_TIERS, SUPPORTED_URGENCY


class ValidationError(Exception):
    """Controlled validation error for quote requests."""


@dataclass
class QuoteRequest:
    industry_id: str
    region: str = ""
    urgency: str = "standard"
    rooms: int = 0
    bathrooms: int = 0
    quantity_fields: dict[str, float] = field(default_factory=dict)
    selected_addons: list[str] = field(default_factory=list)
    scope_text: str = ""
    image_paths: list[str] = field(default_factory=list)
    tier: str = "FREE"
    client_name: str = ""
    client_email: str = ""
    margin_override: float | None = None


QuoteResult = dict[str, Any]


def _safe_int(value: Any, fallback: int = 0) -> int:
    try:
        ivalue = int(value)
    except (TypeError, ValueError):
        return fallback
    return max(ivalue, 0)


def normalize_request(raw: dict[str, Any]) -> QuoteRequest:
    return QuoteRequest(
        industry_id=str(raw.get("industry_id", "")).strip(),
        region=str(raw.get("region", "")).strip() or "DEFAULT",
        urgency=str(raw.get("urgency", "standard")).strip().lower() or "standard",
        rooms=_safe_int(raw.get("rooms", 0)),
        bathrooms=_safe_int(raw.get("bathrooms", 0)),
        quantity_fields=dict(raw.get("quantity_fields", {}) or {}),
        selected_addons=[str(a) for a in (raw.get("selected_addons") or [])],
        scope_text=str(raw.get("scope_text", "") or "").strip(),
        image_paths=[str(p) for p in (raw.get("image_paths") or [])],
        tier=str(raw.get("tier", "FREE") or "FREE").upper(),
        client_name=str(raw.get("client_name", "") or "").strip(),
        client_email=str(raw.get("client_email", "") or "").strip(),
        margin_override=raw.get("margin_override"),
    )


def validate_request(request: QuoteRequest) -> None:
    if not request.industry_id:
        raise ValidationError("industry_id is required")
    if request.rooms < 0 or request.bathrooms < 0:
        raise ValidationError("rooms and bathrooms must be non-negative")
    if request.urgency not in SUPPORTED_URGENCY:
        request.urgency = "standard"
    if request.tier not in SUPPORTED_TIERS:
        request.tier = "FREE"
    if request.margin_override is not None:
        try:
            m = float(request.margin_override)
        except (TypeError, ValueError) as exc:
            raise ValidationError("margin_override must be numeric") from exc
        if not 0 <= m <= 0.95:
            raise ValidationError("margin_override must be between 0 and 0.95")
