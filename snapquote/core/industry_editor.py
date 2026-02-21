from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from core.constants import industries_dir
from core.industry_registry import IndustryRegistry


_REQUIRED = [
    "id",
    "name",
    "currency",
    "base_rate",
    "hourly_rate",
    "inputs",
    "multipliers",
    "addons",
    "tag_rules",
    "margin_default",
    "region_modifiers",
    "urgency_modifiers",
]


def validate_industry(data: dict) -> None:
    for key in _REQUIRED:
        if key not in data:
            raise ValueError(f"Missing required field: {key}")
    if not isinstance(data.get("addons"), dict):
        raise ValueError("addons must be an object")
    if not isinstance(data.get("region_modifiers"), dict):
        raise ValueError("region_modifiers must be an object")
    if not isinstance(data.get("urgency_modifiers"), dict):
        raise ValueError("urgency_modifiers must be an object")


def _version_dir(industry_id: str) -> Path:
    path = industries_dir() / "_versions" / industry_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def save_version(industry_id: str, data: dict) -> Path:
    validate_industry(data)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = _version_dir(industry_id) / f"{stamp}.json"
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return path


def list_versions(industry_id: str) -> list[Path]:
    path = _version_dir(industry_id)
    return sorted(path.glob("*.json"), reverse=True)


def set_active(industry_id: str, data_or_version_path: dict | str | Path) -> Path:
    active_path = industries_dir() / f"{industry_id}.json"
    if isinstance(data_or_version_path, dict):
        data = data_or_version_path
    else:
        data = json.loads(Path(data_or_version_path).read_text(encoding="utf-8"))
    validate_industry(data)
    if active_path.exists():
        save_version(industry_id, json.loads(active_path.read_text(encoding="utf-8")))
    active_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return active_path


def set_active_and_reload(registry: IndustryRegistry, industry_id: str, data_or_version_path: dict | str | Path) -> Path:
    path = set_active(industry_id, data_or_version_path)
    registry.reload()
    return path
