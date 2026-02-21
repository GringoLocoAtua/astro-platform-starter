from __future__ import annotations

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
INDUSTRIES_DIR = ROOT_DIR / "industries"
DATA_DIR = ROOT_DIR / "data"
CLIENT_VAULT_PATH = DATA_DIR / "client_vault.json"
DEFAULT_MARGIN = 0.15
SUPPORTED_URGENCY = {"standard", "urgent", "same_day"}
SUPPORTED_TIERS = {"FREE", "PRO"}
