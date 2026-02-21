from __future__ import annotations

import json
from pathlib import Path

from core.constants import SETTINGS_PATH, data_dir


DEFAULT_SETTINGS = {
    "version": "2.1.0",
    "default_tier": "FREE",
    "last_selected_industry": "cleaning",
    "last_region": "DEFAULT",
    "last_urgency": "standard",
    "last_tier": "FREE",
    "pro_footer_enabled": False,
    "branding": {
        "business_name": "",
        "phone": "",
        "email": "",
        "logo_path": "",
    },
}


def _settings_path() -> Path:
    data_dir().mkdir(parents=True, exist_ok=True)
    return SETTINGS_PATH


def load_settings() -> dict:
    path = _settings_path()
    if not path.exists():
        save_settings(DEFAULT_SETTINGS)
        return dict(DEFAULT_SETTINGS)
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        save_settings(DEFAULT_SETTINGS)
        return dict(DEFAULT_SETTINGS)
    merged = dict(DEFAULT_SETTINGS)
    merged.update(loaded)
    branding = dict(DEFAULT_SETTINGS["branding"])
    branding.update(loaded.get("branding", {}))
    merged["branding"] = branding
    return merged


def save_settings(settings: dict) -> None:
    path = _settings_path()
    payload = dict(DEFAULT_SETTINGS)
    payload.update(settings or {})
    branding = dict(DEFAULT_SETTINGS["branding"])
    branding.update(payload.get("branding", {}))
    payload["branding"] = branding

    temp_path = path.with_suffix(".tmp")
    temp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    temp_path.replace(path)
