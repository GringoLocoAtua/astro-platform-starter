from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field

from core.constants import DATA_DIR, SETTINGS_PATH


@dataclass
class BrandingSettings:
    business_name: str = ""
    email: str = ""
    phone: str = ""
    logo_path: str = ""


@dataclass
class PdfSettings:
    show_footer: bool = True
    watermark_enabled: bool = True
    footer_text: str = "Powered by BU1ST SnapQuote™"


@dataclass
class SecuritySettings:
    require_login: bool = True
    auto_lock_minutes: int = 0


@dataclass
class AppSettings:
    app_version: str = "2.2.0"
    tier: str = "FREE"
    language: str = "en"
    currency: str = "AUD"
    currency_rates: dict[str, float] = field(default_factory=dict)
    theme: str = "dark"
    favorites_industries: list[str] = field(default_factory=list)
    last_industry_id: str = "cleaning"
    last_region: str = "DEFAULT"
    last_urgency: str = "standard"
    branding: BrandingSettings = field(default_factory=BrandingSettings)
    pdf: PdfSettings = field(default_factory=PdfSettings)
    security: SecuritySettings = field(default_factory=SecuritySettings)


def _ensure_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not SETTINGS_PATH.exists():
        save_settings(asdict(AppSettings()))


def _coerce(raw: dict) -> dict:
    defaults = asdict(AppSettings())
    out = dict(defaults)
    out.update(raw or {})
    for section in ("branding", "pdf", "security"):
        merged = dict(defaults[section])
        merged.update(out.get(section, {}))
        out[section] = merged
    out["favorites_industries"] = list((out.get("favorites_industries") or [])[:10])
    return out


def load_settings() -> dict:
    _ensure_file()
    try:
        raw = json.loads(SETTINGS_PATH.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        raw = {}
    data = _coerce(raw)
    save_settings(data)
    return data


def save_settings(settings: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = _coerce(settings)
    # tier defaults for pdf flags
    if payload.get("tier") == "PRO":
        payload["pdf"].setdefault("show_footer", False)
        payload["pdf"].setdefault("watermark_enabled", False)
    tmp = SETTINGS_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, indent=2), encoding="utf-8-sig")
    tmp.replace(SETTINGS_PATH)


def update_settings(partial: dict) -> dict:
    current = load_settings()
    for key, value in partial.items():
        if isinstance(value, dict) and isinstance(current.get(key), dict):
            current[key].update(value)
        else:
            current[key] = value
    save_settings(current)
    return current
