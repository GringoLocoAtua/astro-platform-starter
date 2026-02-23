from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from core.constants import DATA_DIR

QUOTE_STORE_PATH = DATA_DIR / "quotes.json"


def _ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not QUOTE_STORE_PATH.exists():
        QUOTE_STORE_PATH.write_text("[]", encoding="utf-8-sig")


def _read_all() -> list[dict]:
    _ensure_store()
    try:
        data = json.loads(QUOTE_STORE_PATH.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError:
        data = []
    return data if isinstance(data, list) else []


def _write_all(items: list[dict]) -> None:
    QUOTE_STORE_PATH.write_text(json.dumps(items, indent=2), encoding="utf-8-sig")


def save_quote(quote_dict: dict) -> dict:
    items = _read_all()
    payload = dict(quote_dict)
    payload.setdefault("id", str(uuid4()))
    payload.setdefault("saved_at", datetime.now(timezone.utc).isoformat())
    items.append(payload)
    _write_all(items)
    return payload


def list_quotes() -> list[dict]:
    return sorted(_read_all(), key=lambda q: q.get("saved_at", ""), reverse=True)


def load_quote(quote_id: str) -> dict | None:
    for item in _read_all():
        if item.get("id") == quote_id:
            return item
    return None


def delete_quote(quote_id: str) -> bool:
    items = _read_all()
    remaining = [item for item in items if item.get("id") != quote_id]
    if len(remaining) == len(items):
        return False
    _write_all(remaining)
    return True
