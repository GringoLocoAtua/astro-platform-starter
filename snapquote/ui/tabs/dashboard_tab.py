from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.components import Card, GhostButton, PrimaryButton, SecondaryButton


class DashboardTab(QWidget):
    open_new_quote = pyqtSignal()
    open_library = pyqtSignal()
    open_pricing = pyqtSignal()
    open_settings = pyqtSignal()
    open_profile = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        card = Card()
        card.content_layout.addWidget(QLabel("Dashboard"))

        row1 = QHBoxLayout()
        self.new_quote_btn = PrimaryButton("New Quote")
        self.library_btn = SecondaryButton("Quote Library")
        self.pricing_btn = SecondaryButton("Pricing Studio")
        row1.addWidget(self.new_quote_btn)
        row1.addWidget(self.library_btn)
        row1.addWidget(self.pricing_btn)

        row2 = QHBoxLayout()
        self.settings_btn = GhostButton("Settings")
        self.profile_btn = GhostButton("Profile / Login")
        row2.addWidget(self.settings_btn)
        row2.addWidget(self.profile_btn)

        self.last_quote_label = QLabel("Last quote: none")
        self.last_quote_label.setObjectName("subtitle")

        card.content_layout.addLayout(row1)
        card.content_layout.addLayout(row2)
        card.content_layout.addWidget(self.last_quote_label)
        root.addWidget(card)
        root.addStretch(1)

        self.new_quote_btn.clicked.connect(self.open_new_quote.emit)
        self.library_btn.clicked.connect(self.open_library.emit)
        self.pricing_btn.clicked.connect(self.open_pricing.emit)
        self.settings_btn.clicked.connect(self.open_settings.emit)
        self.profile_btn.clicked.connect(self.open_profile.emit)

    def set_last_quote_summary(self, text: str) -> None:
        self.last_quote_label.setText(text)
