from __future__ import annotations

import json
from pathlib import Path

from core.constants import INDUSTRIES_DIR


class IndustryRegistry:
    def __init__(self, industries_path: Path | None = None) -> None:
        self.industries_path = industries_path or INDUSTRIES_DIR
        self._industries: dict[str, dict] = {}
        self._load_all()

    def _load_all(self) -> None:
        if not self.industries_path.exists():
            raise FileNotFoundError(f"Industries directory not found: {self.industries_path}")

        for file_path in sorted(self.industries_path.glob("*.json")):
            with file_path.open("r", encoding="utf-8") as fh:
                payload = json.load(fh)
            normalized = self._validate_and_normalize(payload, file_path)
            self._industries[normalized["id"]] = normalized

        if not self._industries:
            raise ValueError("No industry JSON files found")

    def _validate_and_normalize(self, data: dict, file_path: Path) -> dict:
        required = ["id", "name", "currency", "base_rate", "hourly_rate", "inputs", "multipliers", "addons", "tag_rules", "margin_default", "region_modifiers", "urgency_modifiers"]
        for key in required:
            if key not in data:
                raise ValueError(f"Missing required key '{key}' in {file_path.name}")
        data.setdefault("multipliers", {})
        data.setdefault("addons", {})
        data.setdefault("tag_rules", {})
        data.setdefault("region_modifiers", {})
        data.setdefault("urgency_modifiers", {})
        data.setdefault("margin_default", 0.15)
        return data

    def list_industries(self) -> list[dict[str, str]]:
        return [{"id": value["id"], "name": value["name"]} for value in self._industries.values()]

    def get_industry(self, industry_id: str) -> dict:
        if industry_id not in self._industries:
            raise KeyError(f"Unknown industry '{industry_id}'. Available: {', '.join(sorted(self._industries))}")
        return self._industries[industry_id]
