from __future__ import annotations

from PyQt6.QtWidgets import QVBoxLayout, QWidget

from ui.settings_panel import SettingsPanel


class SettingsTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.panel = SettingsPanel()
        layout.addWidget(self.panel)
