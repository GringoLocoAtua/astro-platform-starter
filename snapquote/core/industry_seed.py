from __future__ import annotations

import json
from pathlib import Path

from core.constants import INDUSTRIES_DIR


def _default_industry(entry: dict) -> dict:
    return {
        "id": entry["id"],
        "name": entry["name"],
        "group": entry.get("group", "Other"),
        "currency": "AUD",
        "base_rate": 110,
        "hourly_rate": 70,
        "min_charge": 90,
        "inputs": {"rooms": 0, "bathrooms": 0},
        "quantity_fields": {},
        "multipliers": {"rooms_rate": 20, "bathrooms_rate": 25},
        "addons": {"priority_support": 35, "materials": 40},
        "tag_rules": {},
        "tag_effects": {},
        "margin_default": 0.15,
        "region_modifiers": {"DEFAULT": 1.0, "NSW": 1.04, "VIC": 1.03, "QLD": 1.0, "NZ": 1.08, "NZ-AUCKLAND": 1.1},
        "urgency_modifiers": {"standard": 1.0, "urgent": 1.12, "same_day": 1.25},
        "defaults": {"region": "DEFAULT", "urgency": "standard"},
    }


def ensure_industry_pack() -> None:
    INDUSTRIES_DIR.mkdir(parents=True, exist_ok=True)
    catalog_path = INDUSTRIES_DIR / "_catalog.json"
    if not catalog_path.exists():
        return
    catalog = json.loads(catalog_path.read_text(encoding="utf-8-sig"))
    for entry in catalog:
        fp = INDUSTRIES_DIR / f"{entry['id']}.json"
        if fp.exists():
            continue
        fp.write_text(json.dumps(_default_industry(entry), indent=2), encoding="utf-8-sig")
