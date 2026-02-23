from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLineEdit,
    QScrollArea,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ui.components import Card, ChipButton, FlowLayout, SectionHeader


class QuoteForm(QWidget):
    inputs_changed = pyqtSignal()
    quote_inputs_changed = inputs_changed

    def __init__(self, industries: list[dict]) -> None:
        super().__init__()
        self._image_paths: list[str] = []
        self._addon_chips: dict[str, ChipButton] = {}
        self._setup_ui(industries)

    def _setup_ui(self, industries: list[dict]) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        self.industry = QLineEdit()
        self.industry.setReadOnly(True)
        self.industry_id_value = industries[0]["id"] if industries else ""

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        content = QVBoxLayout(container)

        basics = Card()
        basics.content_layout.addWidget(SectionHeader("Job Basics", "Core details for accurate pricing"))
        basics_form = QFormLayout()
        self.rooms = QSpinBox(); self.rooms.setRange(0, 100)
        self.bathrooms = QSpinBox(); self.bathrooms.setRange(0, 100)
        self.scope = QTextEdit(); self.scope.setPlaceholderText("Describe scope and outcomes...")
        basics_form.addRow("Rooms", self.rooms)
        basics_form.addRow("Bathrooms", self.bathrooms)
        basics_form.addRow("Scope", self.scope)
        basics.content_layout.addLayout(basics_form)

        addons = Card()
        addons.content_layout.addWidget(SectionHeader("Add-ons", "Select optional services"))
        self.addon_search = QLineEdit(); self.addon_search.setPlaceholderText("Search add-ons...")
        addons.content_layout.addWidget(self.addon_search)
        chip_holder = QWidget()
        self.addon_flow = FlowLayout(chip_holder, h_spacing=8, v_spacing=8)
        addons.content_layout.addWidget(chip_holder)

        client = Card()
        client.content_layout.addWidget(SectionHeader("Client", "Optional for vault history"))
        client_form = QFormLayout()
        self.client_name = QLineEdit()
        self.client_email = QLineEdit()
        client_form.addRow("Name", self.client_name)
        client_form.addRow("Email", self.client_email)
        client.content_layout.addLayout(client_form)

        content.addWidget(basics)
        content.addWidget(addons)
        content.addWidget(client)
        content.addStretch(1)

        scroll.setWidget(container)
        root.addWidget(scroll)

        self.region = QLineEdit("DEFAULT")
        self.urgency = QLineEdit("standard")
        self.tier = QLineEdit("FREE")

        self._connect_signals()

    def _connect_signals(self) -> None:
        self.rooms.valueChanged.connect(self.inputs_changed.emit)
        self.bathrooms.valueChanged.connect(self.inputs_changed.emit)
        self.scope.textChanged.connect(self.inputs_changed.emit)
        self.client_name.textChanged.connect(self.inputs_changed.emit)
        self.client_email.textChanged.connect(self.inputs_changed.emit)
        self.addon_search.textChanged.connect(self._filter_addons)
        self.region.textChanged.connect(self.inputs_changed.emit)
        self.urgency.textChanged.connect(self.inputs_changed.emit)
        self.tier.textChanged.connect(self.inputs_changed.emit)

    def _filter_addons(self) -> None:
        term = self.addon_search.text().strip().lower()
        for key, chip in self._addon_chips.items():
            chip.setVisible(term in key.lower())

    def _rebuild_addon_chips(self, addon_keys: list[str], selected: set[str]) -> None:
        while self.addon_flow.count():
            item = self.addon_flow.takeAt(0)
            widget = item.widget() if item else None
            if widget:
                widget.deleteLater()
        self._addon_chips = {}
        for key in addon_keys:
            chip = ChipButton(key, checked=(key in selected))
            chip.toggled.connect(self.inputs_changed.emit)
            self._addon_chips[key] = chip
            self.addon_flow.addWidget(chip)

    def set_images(self, image_paths: list[str]) -> None:
        self._image_paths = list(image_paths)
        self.inputs_changed.emit()

    def refresh_industries(self, industries: list[dict]) -> None:
        if industries:
            selected_id = self.industry_id_value if any(i["id"] == self.industry_id_value for i in industries) else industries[0]["id"]
            selected = next(i for i in industries if i["id"] == selected_id)
            self.industry_id_value = selected["id"]
            self.industry.setText(selected["name"])
            self.inputs_changed.emit()

    def set_active_selections(self, industry_id: str, industry_name: str, region: str, urgency: str, tier: str) -> None:
        self.industry_id_value = industry_id
        self.industry.setText(industry_name)
        self.region.setText(region)
        self.urgency.setText(urgency)
        self.tier.setText(tier)

    def set_addons(self, addon_keys: list[str]) -> None:
        selected = {k for k, chip in self._addon_chips.items() if chip.isChecked()}
        self._rebuild_addon_chips(addon_keys, selected)
        self._filter_addons()
        self.inputs_changed.emit()

    def clear_form(self) -> None:
        self.rooms.setValue(0)
        self.bathrooms.setValue(0)
        self.scope.clear()
        self.client_name.clear()
        self.client_email.clear()
        self._image_paths = []
        for chip in self._addon_chips.values():
            chip.setChecked(False)
        self.inputs_changed.emit()

    def get_request_dict(self) -> dict:
        return {
            "industry_id": self.industry_id_value,
            "region": self.region.text().strip() or "DEFAULT",
            "urgency": self.urgency.text().strip() or "standard",
            "rooms": self.rooms.value(),
            "bathrooms": self.bathrooms.value(),
            "quantity_fields": {},
            "selected_addons": [k for k, chip in self._addon_chips.items() if chip.isChecked()],
            "scope_text": self.scope.toPlainText(),
            "image_paths": list(self._image_paths),
            "tier": self.tier.text().strip().upper() or "FREE",
            "client_name": self.client_name.text(),
            "client_email": self.client_email.text(),
        }

    def values(self) -> dict:
        return self.get_request_dict()
