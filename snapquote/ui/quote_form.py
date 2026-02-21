from __future__ import annotations

from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class QuoteForm(QWidget):
    def __init__(self, industries: list[dict]) -> None:
        super().__init__()
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

        self.rooms = QSpinBox(); self.rooms.setMinimum(0); self.rooms.setMaximum(100)
        self.bathrooms = QSpinBox(); self.bathrooms.setMinimum(0); self.bathrooms.setMaximum(100)
        self.client_name = QLineEdit()
        self.client_email = QLineEdit()
        self.scope = QTextEdit()
        self.scope.setPlaceholderText("Describe scope...")

        self.addons = QListWidget()
        self.addons.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        self.images = QListWidget()
        self.upload_btn = QPushButton("Upload Images")
        self.upload_btn.clicked.connect(self._upload_images)

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

        upload_wrap = QHBoxLayout()
        upload_wrap.addWidget(self.upload_btn)
        upload_wrap.addWidget(QLabel("Selected Images"))
        root.addWidget(form_box)
        root.addLayout(upload_wrap)
        root.addWidget(self.images)

    def set_addons(self, addon_keys: list[str]) -> None:
        self.addons.clear()
        for key in addon_keys:
            self.addons.addItem(QListWidgetItem(key))

    def _upload_images(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(self, "Choose images")
        for file in files:
            self.images.addItem(file)

    def clear_form(self) -> None:
        self.rooms.setValue(0)
        self.bathrooms.setValue(0)
        self.scope.clear()
        self.client_name.clear()
        self.client_email.clear()
        self.images.clear()
        for index in range(self.addons.count()):
            item = self.addons.item(index)
            item.setSelected(False)

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
            "image_paths": [self.images.item(i).text() for i in range(self.images.count())],
            "tier": self.tier.currentText(),
            "client_name": self.client_name.text(),
            "client_email": self.client_email.text(),
        }
