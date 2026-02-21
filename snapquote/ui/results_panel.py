from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget

from ui.components import Card, ChipButton, SectionHeader


GROUP_ORDER = ["Base", "Quantities", "Add-ons", "Tag Effects", "Modifiers", "Discounts", "Margin", "Other"]


class ResultsPanel(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        total_card = Card()
        total_card.content_layout.addWidget(SectionHeader("Live Quote", "Instant preview of final price"))
        self.total = QLabel("AUD 0.00")
        self.total.setObjectName("totalValue")
        self.total_sub = QLabel("Total incl. margin")
        self.total_sub.setObjectName("subtitle")
        total_card.content_layout.addWidget(self.total)
        total_card.content_layout.addWidget(self.total_sub)

        breakdown_card = Card()
        breakdown_card.content_layout.addWidget(SectionHeader("Breakdown", "Grouped pricing components"))
        self.breakdown_tree = QTreeWidget()
        self.breakdown_tree.setHeaderLabels(["Item", "Amount"])
        self.breakdown_tree.setRootIsDecorated(True)
        self.breakdown_tree.setAlternatingRowColors(True)
        breakdown_card.content_layout.addWidget(self.breakdown_tree)

        details_row = QWidget()
        details_layout = QVBoxLayout(details_row)
        details_layout.setContentsMargins(0, 0, 0, 0)

        self.modifiers_card = Card()
        self.modifiers_card.content_layout.addWidget(SectionHeader("Modifiers"))
        self.modifiers_wrap = QWidget()
        self.modifiers_layout = QVBoxLayout(self.modifiers_wrap)
        self.modifiers_layout.setContentsMargins(0, 0, 0, 0)
        self.modifiers_card.content_layout.addWidget(self.modifiers_wrap)

        self.assumptions_card = Card()
        self.assumptions_card.content_layout.addWidget(SectionHeader("Assumptions"))
        self.assumptions_wrap = QWidget()
        self.assumptions_layout = QVBoxLayout(self.assumptions_wrap)
        self.assumptions_layout.setContentsMargins(0, 0, 0, 0)
        self.assumptions_card.content_layout.addWidget(self.assumptions_wrap)

        details_layout.addWidget(self.modifiers_card)
        details_layout.addWidget(self.assumptions_card)

        layout.addWidget(total_card)
        layout.addWidget(breakdown_card, 1)
        layout.addWidget(details_row)

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

    def _clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def set_quote_result(self, quote: dict) -> None:
        if "error" in quote:
            self.total.setText("Error")
            self.total_sub.setText(str(quote.get("error", "Unknown error")))
            return

        currency = quote.get('display_currency', quote.get('currency', 'AUD'))
        amount = quote.get('display_total', quote.get('total', 0))
        self.total.setText(f"{currency} {amount:.2f}")
        self.total_sub.setText("Total incl. margin")

        grouped: dict[str, list[dict]] = {}
        for item in quote.get("breakdown", []):
            grouped.setdefault(self._infer_group(item), []).append(item)

        self.breakdown_tree.clear()
        for group in GROUP_ORDER:
            items = grouped.get(group)
            if not items:
                continue
            group_node = QTreeWidgetItem([group, ""])
            self.breakdown_tree.addTopLevelItem(group_node)
            for row in items:
                child = QTreeWidgetItem([str(row.get("item", "")), f"{row.get('amount', 0):.2f}"])
                group_node.addChild(child)
            group_node.setExpanded(True)

        self._clear_layout(self.modifiers_layout)
        modifiers = quote.get("applied_modifiers", {})
        if not modifiers:
            self.modifiers_layout.addWidget(QLabel("No modifiers applied"))
        else:
            for key, value in modifiers.items():
                chip = ChipButton(f"{key}: {value}")
                chip.setCheckable(False)
                self.modifiers_layout.addWidget(chip)

        self._clear_layout(self.assumptions_layout)
        assumptions = quote.get("assumptions", [])
        if not assumptions:
            self.assumptions_layout.addWidget(QLabel("No assumptions"))
        else:
            for entry in assumptions:
                self.assumptions_layout.addWidget(QLabel(f"• {entry}"))

    def show_quote(self, quote: dict) -> None:
        self.set_quote_result(quote)
