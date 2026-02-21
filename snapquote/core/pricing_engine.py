from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from core.recurring_detector import is_recurring
from core.region_modifier import resolve_region_multiplier, resolve_urgency_multiplier
from core.validation import QuoteRequest, QuoteResult, ValidationError, validate_request


money = lambda x: round(float(x), 2)


def calculate_quote(request: QuoteRequest, registry, image_tags: list[str]) -> QuoteResult:
    validate_request(request)
    industry = registry.get_industry(request.industry_id)

    subtotal = 0.0
    discounts = 0.0
    assumptions: list[str] = []
    breakdown: list[dict] = []
    applied_tag_effects: list[str] = []

    base_rate = float(industry.get("base_rate", 0.0))
    subtotal += base_rate
    breakdown.append({"item": "Base Service", "amount": base_rate})

    multipliers = industry.get("multipliers", {})
    rooms_amount = request.rooms * float(multipliers.get("rooms_rate", 0.0))
    bathrooms_amount = request.bathrooms * float(multipliers.get("bathrooms_rate", 0.0))
    if rooms_amount:
        subtotal += rooms_amount
        breakdown.append({"item": "Rooms", "amount": rooms_amount, "meta": {"rooms": request.rooms}})
    if bathrooms_amount:
        subtotal += bathrooms_amount
        breakdown.append({"item": "Bathrooms", "amount": bathrooms_amount, "meta": {"bathrooms": request.bathrooms}})

    addons = industry.get("addons", {})
    chosen_addons = set(request.selected_addons)
    for addon in request.selected_addons:
        if addon in addons:
            value = float(addons[addon])
            subtotal += value
            breakdown.append({"item": f"Addon: {addon}", "amount": value})
        else:
            assumptions.append(f"Unknown addon ignored: {addon}")

    tag_rules = industry.get("tag_rules", {})
    for tag in image_tags:
        rule = tag_rules.get(tag)
        if tag in addons and tag not in chosen_addons:
            value = float(addons[tag])
            subtotal += value
            breakdown.append({"item": f"Tag Addon: {tag}", "amount": value})
            chosen_addons.add(tag)
            applied_tag_effects.append(f"included addon {tag}")
        if isinstance(rule, dict):
            rtype = rule.get("type")
            if rtype == "include_addon":
                addon_name = rule.get("addon")
                if addon_name in addons and addon_name not in chosen_addons:
                    value = float(addons[addon_name])
                    subtotal += value
                    breakdown.append({"item": f"Tag Addon: {addon_name}", "amount": value})
                    chosen_addons.add(addon_name)
                    applied_tag_effects.append(f"included addon {addon_name}")
            elif rtype == "multiplier":
                factor = float(rule.get("value", 1.0))
                pre = subtotal
                subtotal *= factor
                uplift = subtotal - pre
                label = str(rule.get("label", f"Tag Multiplier {tag}"))
                breakdown.append({"item": label, "amount": uplift, "meta": {"factor": factor}})
                applied_tag_effects.append(f"multiplied by {factor} for {tag}")

    region_multiplier = resolve_region_multiplier(industry, request.region)
    subtotal *= region_multiplier
    breakdown.append({"item": f"Region Modifier ({request.region}) x{region_multiplier}", "amount": 0.0})

    urgency_multiplier = resolve_urgency_multiplier(industry, request.urgency)
    subtotal *= urgency_multiplier
    breakdown.append({"item": f"Urgency ({request.urgency}) x{urgency_multiplier}", "amount": 0.0})

    recurring_discount = 0.0
    if is_recurring(request.scope_text):
        recurring_discount = subtotal * 0.10
        subtotal -= recurring_discount
        discounts += recurring_discount
        breakdown.append({"item": "Recurring Discount (10%)", "amount": -recurring_discount})

    margin_rate = float(request.margin_override if request.margin_override is not None else industry.get("margin_default", 0.0))
    margin_amount = subtotal * margin_rate
    total = subtotal + margin_amount
    breakdown.append({"item": f"Margin ({margin_rate * 100:.0f}%)", "amount": margin_amount})

    return {
        "quote_id": str(uuid4()),
        "industry_id": request.industry_id,
        "currency": industry.get("currency", "AUD"),
        "subtotal": money(subtotal),
        "discounts": money(discounts),
        "margin_amount": money(margin_amount),
        "total": money(total),
        "breakdown": [{**item, "amount": money(item["amount"])} for item in breakdown],
        "applied_modifiers": {
            "region_multiplier": region_multiplier,
            "urgency_multiplier": urgency_multiplier,
            "recurring_discount": money(recurring_discount),
            "tag_effects": applied_tag_effects,
        },
        "assumptions": assumptions,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
