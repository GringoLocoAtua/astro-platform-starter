from __future__ import annotations

import sys
from pathlib import Path

DEFAULT_REGION = "DEFAULT"
DEFAULT_URGENCY = "standard"
DEFAULT_TIER = "FREE"
SUPPORTED_TIERS = {"FREE", "PRO"}
SUPPORTED_URGENCY = {"standard", "urgent", "same_day"}


def app_root() -> Path:
    if getattr(sys, "frozen", False) and getattr(sys, "_MEIPASS", None):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[1]


def industries_dir() -> Path:
    return app_root() / "industries"


def assets_dir() -> Path:
    return app_root() / "assets"


def data_dir() -> Path:
    return app_root() / "data"


ROOT_DIR = app_root()
INDUSTRIES_DIR = industries_dir()
ASSETS_DIR = assets_dir()
DATA_DIR = data_dir()
CLIENT_VAULT_PATH = DATA_DIR / "client_vault.json"
SETTINGS_PATH = DATA_DIR / "settings.json"
RATES_PATH = DATA_DIR / "rates.json"
USERS_PATH = DATA_DIR / "users.json"
SESSION_PATH = DATA_DIR / "session.json"
DEFAULT_MARGIN = 0.15
