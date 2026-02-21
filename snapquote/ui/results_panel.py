from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QListWidget, QVBoxLayout, QWidget


class ResultsPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        self.total = QLabel("Total: -")
        self.total.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.breakdown = QListWidget()
        self.modifiers = QListWidget()
        self.assumptions = QListWidget()

        layout.addWidget(self.total)
        layout.addWidget(QLabel("Grouped Breakdown"))
        layout.addWidget(self.breakdown)
        layout.addWidget(QLabel("Modifiers"))
        layout.addWidget(self.modifiers)
        layout.addWidget(QLabel("Assumptions"))
        layout.addWidget(self.assumptions)

    def _infer_group(self, item: dict) -> str:
        meta = item.get("meta", {})
        if isinstance(meta, dict) and meta.get("group"):
            return meta["group"]
        text = str(item.get("item", "")).lower()
        if text.startswith("base"):
            return "Base"
        if text.startswith("rooms") or text.startswith("bathrooms"):
            return "Quantities"
        if "addon" in text:
            return "Add-ons"
        if "tag" in text or "uplift" in text:
            return "Tag Effects"
        if "modifier" in text or "urgency" in text or "region" in text:
            return "Modifiers"
        if "discount" in text:
            return "Discounts"
        if "margin" in text:
            return "Margin"
        return "Other"

    def show_quote(self, quote: dict) -> None:
        if "error" in quote:
            self.total.setText(f"Error: {quote['error']}")
            return
        self.total.setText(f"Total: {quote.get('currency', 'AUD')} {quote.get('total', 0):.2f}")
        groups: dict[str, list[str]] = {}
        for item in quote.get("breakdown", []):
            group = self._infer_group(item)
            groups.setdefault(group, []).append(f"{item.get('item')}: {item.get('amount'):.2f}")

        self.breakdown.clear()
        for group in ["Base", "Quantities", "Add-ons", "Tag Effects", "Modifiers", "Discounts", "Margin", "Other"]:
            if group not in groups:
                continue
            self.breakdown.addItem(f"[{group}]")
            for line in groups[group]:
                self.breakdown.addItem(f"  - {line}")

        self.modifiers.clear()
        for key, value in quote.get("applied_modifiers", {}).items():
            self.modifiers.addItem(f"{key}: {value}")

        self.assumptions.clear()
        for line in quote.get("assumptions", []):
            self.assumptions.addItem(line)
