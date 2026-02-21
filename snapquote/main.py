from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtWidgets import QApplication

from ui.main_window import MainWindow


def ensure_data_dir() -> None:
    Path(__file__).resolve().parent.joinpath("data").mkdir(parents=True, exist_ok=True)


def main() -> int:
    ensure_data_dir()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
