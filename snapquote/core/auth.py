from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta

from core.constants import DATA_DIR, SESSION_PATH, USERS_PATH


def _ensure() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not USERS_PATH.exists():
        USERS_PATH.write_text(json.dumps({"users": []}, indent=2), encoding="utf-8")


def _load_users() -> dict:
    _ensure()
    try:
        return json.loads(USERS_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"users": []}


def _save_users(payload: dict) -> None:
    USERS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def has_users() -> bool:
    return len(_load_users().get("users", [])) > 0


def _hash_password(password: str, salt: bytes) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120_000).hex()


def create_user(username: str, password: str, is_admin: bool = False) -> None:
    payload = _load_users()
    users = payload.setdefault("users", [])
    if any(u["username"].lower() == username.lower() for u in users):
        raise ValueError("User already exists")
    salt = os.urandom(16)
    users.append(
        {
            "username": username,
            "salt": salt.hex(),
            "password_hash": _hash_password(password, salt),
            "is_admin": is_admin,
        }
    )
    _save_users(payload)


def verify_user(username: str, password: str) -> bool:
    payload = _load_users()
    for user in payload.get("users", []):
        if user["username"].lower() == username.lower():
            salt = bytes.fromhex(user["salt"])
            expected = user["password_hash"]
            return hmac.compare_digest(expected, _hash_password(password, salt))
    return False


def save_session(username: str) -> None:
    SESSION_PATH.write_text(json.dumps({"username": username, "last_active": datetime.utcnow().isoformat()}), encoding="utf-8")


def load_session() -> dict:
    if not SESSION_PATH.exists():
        return {}
    try:
        return json.loads(SESSION_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def clear_session() -> None:
    if SESSION_PATH.exists():
        SESSION_PATH.unlink()


def is_session_locked(auto_lock_minutes: int) -> bool:
    if auto_lock_minutes <= 0:
        return False
    session = load_session()
    last_active = session.get("last_active")
    if not last_active:
        return True
    try:
        ts = datetime.fromisoformat(last_active)
    except ValueError:
        return True
    return datetime.utcnow() > ts + timedelta(minutes=auto_lock_minutes)
