from __future__ import annotations

import json
from datetime import datetime, timezone

from core.constants import CLIENT_VAULT_PATH, DATA_DIR


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not CLIENT_VAULT_PATH.exists():
        CLIENT_VAULT_PATH.write_text("{}", encoding="utf-8-sig")


def _read_store() -> dict:
    _ensure_store()
    try:
        return json.loads(CLIENT_VAULT_PATH.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        return {}


def save_quote(client_name: str, quote_result: dict) -> None:
    if not client_name:
        return
    store = _read_store()
    store.setdefault(client_name, [])
    payload = dict(quote_result)
    payload["saved_at"] = datetime.now(timezone.utc).isoformat()
    store[client_name].append(payload)
    CLIENT_VAULT_PATH.write_text(json.dumps(store, indent=2), encoding="utf-8-sig")


def get_client_history(client_name: str) -> list[dict]:
    if not client_name:
        return []
    store = _read_store()
    return list(store.get(client_name, []))
