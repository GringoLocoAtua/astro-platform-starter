from __future__ import annotations

import json
from pathlib import Path

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.industry_editor import list_versions, save_version, set_active, validate_industry
from core.industry_registry import IndustryRegistry
from core.quote_builder import build_quote


class PricingStudio(QWidget):
    active_industry_changed = pyqtSignal()

    def __init__(self, registry: IndustryRegistry) -> None:
        super().__init__()
        self.registry = registry
        self._setup_ui()
        self.refresh_industry_list()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)

        top = QHBoxLayout()
        self.industry_select = QComboBox()
        self.load_btn = QPushButton("Load")
        top.addWidget(QLabel("Industry"))
        top.addWidget(self.industry_select)
        top.addWidget(self.load_btn)
        root.addLayout(top)

        rates_box = QGroupBox("Rates")
        rates_form = QFormLayout(rates_box)
        self.base_rate = QLineEdit()
        self.hourly_rate = QLineEdit()
        self.margin_default = QLineEdit()
        rates_form.addRow("Base Rate", self.base_rate)
        rates_form.addRow("Hourly Rate", self.hourly_rate)
        rates_form.addRow("Margin Default", self.margin_default)

        self.multipliers = self._map_table(["key", "value"])
        self.region_mod = self._map_table(["region", "multiplier"])
        self.urgency_mod = self._map_table(["urgency", "multiplier"])
        self.addons = self._map_table(["addon", "price"])
        self.tag_rules = self._map_table(["tag", "type", "addon", "value", "label"])

        root.addWidget(rates_box)
        root.addWidget(QLabel("Multipliers"))
        root.addWidget(self.multipliers)
        root.addWidget(QLabel("Region Modifiers"))
        root.addWidget(self.region_mod)
        root.addWidget(QLabel("Urgency Modifiers"))
        root.addWidget(self.urgency_mod)
        root.addWidget(QLabel("Add-ons"))
        root.addWidget(self.addons)
        root.addWidget(QLabel("Tag Rules"))
        root.addWidget(self.tag_rules)

        action_row = QHBoxLayout()
        self.save_version_btn = QPushButton("Save Version")
        self.set_active_btn = QPushButton("Set Active")
        self.set_active_version_btn = QPushButton("Set Active Selected Version")
        action_row.addWidget(self.save_version_btn)
        action_row.addWidget(self.set_active_btn)
        action_row.addWidget(self.set_active_version_btn)
        root.addLayout(action_row)

        self.versions = QListWidget()
        root.addWidget(QLabel("Saved Versions"))
        root.addWidget(self.versions)

        sim_box = QGroupBox("Simulate Quote")
        sim_form = QFormLayout(sim_box)
        self.sim_rooms = QSpinBox(); self.sim_rooms.setRange(0, 100)
        self.sim_baths = QSpinBox(); self.sim_baths.setRange(0, 100)
        self.sim_region = QLineEdit("DEFAULT")
        self.sim_urgency = QLineEdit("standard")
        self.sim_tags = QLineEdit("")
        self.sim_scope = QLineEdit("")
        self.sim_run = QPushButton("Simulate")
        self.sim_output = QTextEdit(); self.sim_output.setReadOnly(True)
        sim_form.addRow("Rooms", self.sim_rooms)
        sim_form.addRow("Bathrooms", self.sim_baths)
        sim_form.addRow("Region", self.sim_region)
        sim_form.addRow("Urgency", self.sim_urgency)
        sim_form.addRow("Tags (comma)", self.sim_tags)
        sim_form.addRow("Scope", self.sim_scope)
        sim_form.addRow(self.sim_run)
        sim_form.addRow(self.sim_output)
        root.addWidget(sim_box)

        self.load_btn.clicked.connect(self.load_current)
        self.save_version_btn.clicked.connect(self.save_version_action)
        self.set_active_btn.clicked.connect(self.set_active_action)
        self.set_active_version_btn.clicked.connect(self.set_active_selected_version)
        self.sim_run.clicked.connect(self.simulate)

    def _map_table(self, headers: list[str]) -> QTableWidget:
        table = QTableWidget(0, len(headers))
        table.setHorizontalHeaderLabels(headers)
        return table

    def _set_map_rows(self, table: QTableWidget, data: dict) -> None:
        table.setRowCount(0)
        for key, value in data.items():
            row = table.rowCount()
            table.insertRow(row)
            table.setItem(row, 0, QTableWidgetItem(str(key)))
            if table.columnCount() == 2:
                table.setItem(row, 1, QTableWidgetItem(str(value)))

    def _set_tag_rule_rows(self, rules: dict) -> None:
        self.tag_rules.setRowCount(0)
        for tag, rule in rules.items():
            row = self.tag_rules.rowCount()
            self.tag_rules.insertRow(row)
            self.tag_rules.setItem(row, 0, QTableWidgetItem(tag))
            if isinstance(rule, dict):
                self.tag_rules.setItem(row, 1, QTableWidgetItem(str(rule.get("type", ""))))
                self.tag_rules.setItem(row, 2, QTableWidgetItem(str(rule.get("addon", ""))))
                self.tag_rules.setItem(row, 3, QTableWidgetItem(str(rule.get("value", ""))))
                self.tag_rules.setItem(row, 4, QTableWidgetItem(str(rule.get("label", ""))))

    def refresh_industry_list(self) -> None:
        current = self.industry_select.currentData()
        self.industry_select.clear()
        for item in self.registry.list_industries():
            self.industry_select.addItem(item["name"], item["id"])
        idx = max(0, self.industry_select.findData(current))
        self.industry_select.setCurrentIndex(idx)
        self.load_current()

    def load_current(self) -> None:
        industry_id = self.industry_select.currentData()
        if not industry_id:
            return
        data = self.registry.get_industry(industry_id)
        self.base_rate.setText(str(data.get("base_rate", 0)))
        self.hourly_rate.setText(str(data.get("hourly_rate", 0)))
        self.margin_default.setText(str(data.get("margin_default", 0)))
        self._set_map_rows(self.multipliers, data.get("multipliers", {}))
        self._set_map_rows(self.region_mod, data.get("region_modifiers", {}))
        self._set_map_rows(self.urgency_mod, data.get("urgency_modifiers", {}))
        self._set_map_rows(self.addons, data.get("addons", {}))
        self._set_tag_rule_rows(data.get("tag_rules", {}))
        self.refresh_versions(industry_id)
        self.active_industry_changed.emit()

    def _read_map_table(self, table: QTableWidget) -> dict:
        out = {}
        for row in range(table.rowCount()):
            k = table.item(row, 0)
            v = table.item(row, 1)
            if not k or not k.text().strip() or not v:
                continue
            key = k.text().strip()
            text = v.text().strip()
            try:
                out[key] = float(text)
            except ValueError:
                out[key] = text
        return out

    def _read_tag_rules(self) -> dict:
        rules = {}
        for row in range(self.tag_rules.rowCount()):
            tag = self.tag_rules.item(row, 0)
            if not tag or not tag.text().strip():
                continue
            t = self.tag_rules.item(row, 1)
            addon = self.tag_rules.item(row, 2)
            value = self.tag_rules.item(row, 3)
            label = self.tag_rules.item(row, 4)
            rule = {"type": t.text().strip() if t else ""}
            if addon and addon.text().strip():
                rule["addon"] = addon.text().strip()
            if value and value.text().strip():
                try:
                    rule["value"] = float(value.text().strip())
                except ValueError:
                    pass
            if label and label.text().strip():
                rule["label"] = label.text().strip()
            rules[tag.text().strip()] = rule
        return rules

    def get_edited_data(self) -> dict:
        current = self.registry.get_industry(self.industry_select.currentData())
        edited = dict(current)
        edited["base_rate"] = float(self.base_rate.text() or 0)
        edited["hourly_rate"] = float(self.hourly_rate.text() or 0)
        edited["margin_default"] = float(self.margin_default.text() or 0)
        edited["multipliers"] = self._read_map_table(self.multipliers)
        edited["region_modifiers"] = self._read_map_table(self.region_mod)
        edited["urgency_modifiers"] = self._read_map_table(self.urgency_mod)
        edited["addons"] = self._read_map_table(self.addons)
        edited["tag_rules"] = self._read_tag_rules()
        return edited

    def save_version_action(self) -> None:
        try:
            data = self.get_edited_data()
            validate_industry(data)
            path = save_version(data["id"], data)
            self.refresh_versions(data["id"])
            QMessageBox.information(self, "Saved", f"Saved {path.name}")
        except Exception as exc:
            QMessageBox.warning(self, "Save failed", str(exc))

    def set_active_action(self) -> None:
        try:
            data = self.get_edited_data()
            set_active(data["id"], data)
            self.registry.reload()
            self.active_industry_changed.emit()
            self.refresh_industry_list()
            QMessageBox.information(self, "Applied", "Set edited config as active.")
        except Exception as exc:
            QMessageBox.warning(self, "Set active failed", str(exc))

    def set_active_selected_version(self) -> None:
        selected = self.versions.currentItem()
        if not selected:
            return
        path = Path(selected.text())
        industry_id = self.industry_select.currentData()
        try:
            set_active(industry_id, path)
            self.registry.reload()
            self.active_industry_changed.emit()
            self.refresh_industry_list()
            QMessageBox.information(self, "Applied", f"Activated {path.name}")
        except Exception as exc:
            QMessageBox.warning(self, "Set active failed", str(exc))

    def refresh_versions(self, industry_id: str) -> None:
        self.versions.clear()
        for version in list_versions(industry_id):
            self.versions.addItem(str(version))

    def simulate(self) -> None:
        edited = self.get_edited_data()
        tags = [t.strip() for t in self.sim_tags.text().split(",") if t.strip()]
        req = {
            "industry_id": edited["id"],
            "region": self.sim_region.text().strip() or "DEFAULT",
            "urgency": self.sim_urgency.text().strip() or "standard",
            "rooms": self.sim_rooms.value(),
            "bathrooms": self.sim_baths.value(),
            "quantity_fields": {},
            "selected_addons": [],
            "scope_text": self.sim_scope.text(),
            "image_paths": [],
            "tier": "PRO",
            "client_name": "",
            "client_email": "",
        }
        result = build_quote(req, confirmed_tags=tags, industry_override=edited)
        self.sim_output.setPlainText(json.dumps(result, indent=2))
