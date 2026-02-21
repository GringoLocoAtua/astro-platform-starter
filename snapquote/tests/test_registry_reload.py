import json

from core.industry_editor import set_active
from core.industry_registry import IndustryRegistry
from core.quote_builder import build_quote


def test_registry_reload_applies_new_base_rate(tmp_path, monkeypatch):
    industries = tmp_path / "industries"
    industries.mkdir()
    source = {
        "id": "cleaning",
        "name": "Residential Cleaning",
        "currency": "AUD",
        "base_rate": 120,
        "hourly_rate": 70,
        "inputs": {"rooms": 0, "bathrooms": 0},
        "multipliers": {"rooms_rate": 25, "bathrooms_rate": 30},
        "addons": {"oven": 45},
        "tag_rules": {},
        "margin_default": 0.18,
        "region_modifiers": {"DEFAULT": 1.0},
        "urgency_modifiers": {"standard": 1.0},
    }
    (industries / "cleaning.json").write_text(json.dumps(source), encoding="utf-8")

    reg = IndustryRegistry(industries)
    updated = dict(source)
    updated["base_rate"] = 130

    monkeypatch.setattr("core.industry_editor.industries_dir", lambda: industries)
    set_active("cleaning", updated)
    reg.reload()
    assert reg.get_industry("cleaning")["base_rate"] == 130

    req = {
        "industry_id": "cleaning",
        "region": "DEFAULT",
        "urgency": "standard",
        "rooms": 0,
        "bathrooms": 0,
        "selected_addons": [],
        "scope_text": "",
        "image_paths": [],
        "tier": "FREE",
    }

    class DummyRegistry:
        def get_industry(self, industry_id: str) -> dict:
            return updated

    quote = build_quote(req, confirmed_tags=[], industry_override=updated)
    assert quote["subtotal"] == 130
