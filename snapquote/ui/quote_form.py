from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class QuoteForm(QWidget):
    quote_inputs_changed = pyqtSignal()

    def __init__(self, industries: list[dict]) -> None:
        super().__init__()
        self._image_paths: list[str] = []
        self._setup_ui(industries)

    def _setup_ui(self, industries: list[dict]) -> None:
        root = QVBoxLayout(self)

        form_box = QGroupBox("Quote Inputs")
        form = QFormLayout(form_box)

        self.industry = QComboBox()
        for entry in industries:
            self.industry.addItem(entry["name"], entry["id"])

        self.region = QComboBox()
        self.region.addItems(["DEFAULT", "NSW", "VIC", "QLD", "NZ", "NZ-AUCKLAND"])

        self.urgency = QComboBox()
        self.urgency.addItems(["standard", "urgent", "same_day"])

        self.tier = QComboBox()
        self.tier.addItems(["FREE", "PRO"])

        self.rooms = QSpinBox()
        self.rooms.setRange(0, 100)
        self.bathrooms = QSpinBox()
        self.bathrooms.setRange(0, 100)
        self.client_name = QLineEdit()
        self.client_email = QLineEdit()
        self.scope = QTextEdit()
        self.scope.setPlaceholderText("Describe scope...")

        self.addons = QListWidget()
        self.addons.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        form.addRow("Industry", self.industry)
        form.addRow("Region", self.region)
        form.addRow("Urgency", self.urgency)
        form.addRow("Tier", self.tier)
        form.addRow("Rooms", self.rooms)
        form.addRow("Bathrooms", self.bathrooms)
        form.addRow("Add-ons", self.addons)
        form.addRow("Scope", self.scope)
        form.addRow("Client Name", self.client_name)
        form.addRow("Client Email", self.client_email)
        root.addWidget(form_box)

        self._connect_signals()

    def _connect_signals(self) -> None:
        self.industry.currentIndexChanged.connect(self.quote_inputs_changed.emit)
        self.region.currentIndexChanged.connect(self.quote_inputs_changed.emit)
        self.urgency.currentIndexChanged.connect(self.quote_inputs_changed.emit)
        self.tier.currentIndexChanged.connect(self.quote_inputs_changed.emit)
        self.rooms.valueChanged.connect(self.quote_inputs_changed.emit)
        self.bathrooms.valueChanged.connect(self.quote_inputs_changed.emit)
        self.client_name.textChanged.connect(self.quote_inputs_changed.emit)
        self.client_email.textChanged.connect(self.quote_inputs_changed.emit)
        self.scope.textChanged.connect(self.quote_inputs_changed.emit)
        self.addons.itemSelectionChanged.connect(self.quote_inputs_changed.emit)

    def set_images(self, image_paths: list[str]) -> None:
        self._image_paths = list(image_paths)
        self.quote_inputs_changed.emit()

    def refresh_industries(self, industries: list[dict]) -> None:
        current_id = self.industry.currentData()
        self.industry.blockSignals(True)
        self.industry.clear()
        for entry in industries:
            self.industry.addItem(entry["name"], entry["id"])
        idx = max(0, self.industry.findData(current_id))
        self.industry.setCurrentIndex(idx)
        self.industry.blockSignals(False)
        self.quote_inputs_changed.emit()

    def set_addons(self, addon_keys: list[str]) -> None:
        selected = {x.text() for x in self.addons.selectedItems()}
        self.addons.blockSignals(True)
        self.addons.clear()
        for key in addon_keys:
            item = QListWidgetItem(key)
            item.setSelected(key in selected)
            self.addons.addItem(item)
        self.addons.blockSignals(False)
        self.quote_inputs_changed.emit()

    def clear_form(self) -> None:
        self.rooms.setValue(0)
        self.bathrooms.setValue(0)
        self.scope.clear()
        self.client_name.clear()
        self.client_email.clear()
        self._image_paths = []
        for index in range(self.addons.count()):
            self.addons.item(index).setSelected(False)
        self.quote_inputs_changed.emit()

    def values(self) -> dict:
        return {
            "industry_id": self.industry.currentData(),
            "region": self.region.currentText(),
            "urgency": self.urgency.currentText(),
            "rooms": self.rooms.value(),
            "bathrooms": self.bathrooms.value(),
            "quantity_fields": {},
            "selected_addons": [x.text() for x in self.addons.selectedItems()],
            "scope_text": self.scope.toPlainText(),
            "image_paths": list(self._image_paths),
            "tier": self.tier.currentText(),
            "client_name": self.client_name.text(),
            "client_email": self.client_email.text(),
        }
