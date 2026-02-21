from __future__ import annotations

import json
from pathlib import Path

from core.constants import industries_dir
from core.industry_seed import ensure_industry_pack


class IndustryRegistry:
    def __init__(self, industries_path: Path | None = None) -> None:
        self.industries_path = industries_path or industries_dir()
        self._industries: dict[str, dict] = {}
        self._catalog: list[dict] = []
        self._load_all()

    def _load_catalog(self) -> list[dict]:
        path = self.industries_path / "_catalog.json"
        if not path.exists():
            return []
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []

    def _load_all(self) -> None:
        ensure_industry_pack()
        if not self.industries_path.exists():
            raise FileNotFoundError(f"Industries directory not found: {self.industries_path}")

        self._catalog = self._load_catalog()
        catalog_order = {entry.get("id"): idx for idx, entry in enumerate(self._catalog)}

        loaded: dict[str, dict] = {}
        files = [f for f in self.industries_path.glob("*.json") if f.name != "_catalog.json"]
        files.sort(key=lambda p: catalog_order.get(p.stem, 10_000))

        for file_path in files:
            if "_versions" in file_path.parts:
                continue
            with file_path.open("r", encoding="utf-8") as fh:
                payload = json.load(fh)
            normalized = self._validate_and_normalize(payload, file_path)
            loaded[normalized["id"]] = normalized

        if not loaded:
            raise ValueError("No industry JSON files found")
        self._industries = loaded

    def reload(self) -> None:
        self._load_all()

    def _validate_and_normalize(self, data: dict, file_path: Path) -> dict:
        data = dict(data)
        data.setdefault("id", file_path.stem)
        data.setdefault("name", file_path.stem.replace("_", " ").title())
        data.setdefault("group", "Other")
        data.setdefault("currency", "AUD")
        data.setdefault("base_rate", 100)
        data.setdefault("hourly_rate", 60)
        data.setdefault("min_charge", data.get("base_rate", 0))
        data.setdefault("inputs", {})
        data.setdefault("quantity_fields", {})
        data.setdefault("multipliers", {})
        data.setdefault("addons", {})
        data.setdefault("tag_rules", {})
        data.setdefault("margin_default", 0.15)
        data.setdefault("region_modifiers", {"DEFAULT": 1.0})
        data.setdefault("urgency_modifiers", {"standard": 1.0, "urgent": 1.1, "same_day": 1.2})
        return data

    def list_industries(self) -> list[dict[str, str]]:
        return [{"id": value["id"], "name": value["name"], "group": value.get("group", "Other")} for value in self._industries.values()]

    def get_industry(self, industry_id: str) -> dict:
        if industry_id not in self._industries:
            raise KeyError(f"Unknown industry '{industry_id}'. Available: {', '.join(sorted(self._industries))}")
        return self._industries[industry_id]
