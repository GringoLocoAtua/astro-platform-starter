from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from core.auth import is_session_locked
from core.constants import data_dir
from core.settings_store import load_settings
from ui.app_shell import AppShell
from ui.login_dialog import LoginDialog


def ensure_data_dir() -> None:
    data_dir().mkdir(parents=True, exist_ok=True)


def main() -> int:
    ensure_data_dir()
    app = QApplication(sys.argv)

    settings = load_settings()
    if settings.get("security", {}).get("require_login", True):
        if is_session_locked(int(settings.get("security", {}).get("auto_lock_minutes", 0))):
            login = LoginDialog()
            if login.exec() == 0:
                return 0

    window = AppShell()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
