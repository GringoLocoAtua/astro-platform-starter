from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QListWidget, QVBoxLayout, QWidget


class ResultsPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.total = QLabel("Total: -")
        self.breakdown = QListWidget()
        self.modifiers = QListWidget()
        self.assumptions = QListWidget()

        layout.addWidget(self.total)
        layout.addWidget(QLabel("Breakdown"))
        layout.addWidget(self.breakdown)
        layout.addWidget(QLabel("Modifiers"))
        layout.addWidget(self.modifiers)
        layout.addWidget(QLabel("Assumptions"))
        layout.addWidget(self.assumptions)

    def show_quote(self, quote: dict) -> None:
        if "error" in quote:
            self.total.setText(f"Error: {quote['error']}")
            return
        self.total.setText(f"Total: {quote.get('currency', 'AUD')} {quote.get('total', 0):.2f}")
        self.breakdown.clear()
        for item in quote.get("breakdown", []):
            self.breakdown.addItem(f"{item.get('item')}: {item.get('amount'):.2f}")
        self.modifiers.clear()
        for key, value in quote.get("applied_modifiers", {}).items():
            self.modifiers.addItem(f"{key}: {value}")
        self.assumptions.clear()
        for line in quote.get("assumptions", []):
            self.assumptions.addItem(line)
