from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QTimer, pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QSplitter,
    QVBoxLayout,
    QWidget,
    QFileDialog,
)

from core.currency import convert_amount, fetch_rates
from core.industry_registry import IndustryRegistry
from core.quote_store import save_quote
from core.quote_builder import analyze_images, build_quote
from core.settings_store import load_settings, save_settings
from export.pdf_generator import generate_quote_pdf
from ui.components import Card, GhostButton, PrimaryButton, SecondaryButton
from ui.photo_panel import PhotoPanel
from ui.quote_form import QuoteForm
from ui.results_panel import ResultsPanel


class NewQuoteTab(QWidget):
    quote_saved = pyqtSignal(dict)

    def __init__(self, registry: IndustryRegistry):
        super().__init__()
        self.registry = registry
        self.settings = load_settings()
        self.current_quote: dict | None = None
        self.image_tag_cache: dict[str, list[str]] = {}
        self.confirmed_tags: list[str] = []
        self.preview_timer = QTimer(self)
        self.preview_timer.setSingleShot(True)
        self.preview_timer.setInterval(350)
        self.preview_timer.timeout.connect(self._generate_live)
        self._setup_ui()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)

        control_card = Card()
        control_layout = QHBoxLayout()
        self.industry_combo = QComboBox()
        self.industry_combo.setEditable(True)
        self.region_combo = QComboBox(); self.region_combo.addItems(["DEFAULT", "NSW", "VIC", "QLD", "NZ", "NZ-AUCKLAND"])
        self.urgency_combo = QComboBox(); self.urgency_combo.addItems(["standard", "urgent", "same_day"])
        self.tier_combo = QComboBox(); self.tier_combo.addItems(["FREE", "PRO"])
        self.favorite_btn = QPushButton("★")
        control_layout.addWidget(QLabel("Industry")); control_layout.addWidget(self.industry_combo, 3)
        control_layout.addWidget(self.favorite_btn)
        control_layout.addWidget(QLabel("Region")); control_layout.addWidget(self.region_combo)
        control_layout.addWidget(QLabel("Urgency")); control_layout.addWidget(self.urgency_combo)
        control_layout.addWidget(QLabel("Tier")); control_layout.addWidget(self.tier_combo)
        control_card.content_layout.addLayout(control_layout)

        split = QSplitter()
        self.form = QuoteForm(self.registry.list_industries())
        self.results = ResultsPanel()
        self.photo_panel = PhotoPanel()

        # schema fields card
        self.schema_card = Card()
        self.schema_form = QFormLayout()
        self.appliance_type = QComboBox(); self.appliance_type.addItems(["fridge", "dishwasher", "washing_machine", "oven", "dryer"])
        self.fault_type = QComboBox(); self.fault_type.addItems(["not_starting", "leak", "noisy", "temperature_issue", "other"])
        self.callout_fee = QSpinBox(); self.callout_fee.setRange(0, 10000)
        self.labour_hours = QSpinBox(); self.labour_hours.setRange(0, 100)
        self.parts_estimate = QSpinBox(); self.parts_estimate.setRange(0, 10000)
        self.campaign_type = QComboBox(); self.campaign_type.addItems(["search", "display", "shopping", "video"])
        self.monthly_ad_spend = QSpinBox(); self.monthly_ad_spend.setRange(0, 1000000)
        self.setup_fee = QSpinBox(); self.setup_fee.setRange(0, 50000)
        self.ongoing_management = QSpinBox(); self.ongoing_management.setRange(0, 50000)

        self.schema_form.addRow("Appliance Type", self.appliance_type)
        self.schema_form.addRow("Fault Type", self.fault_type)
        self.schema_form.addRow("Callout Fee", self.callout_fee)
        self.schema_form.addRow("Labour Hours", self.labour_hours)
        self.schema_form.addRow("Parts Estimate", self.parts_estimate)
        self.schema_form.addRow("Campaign Type", self.campaign_type)
        self.schema_form.addRow("Monthly Ad Spend", self.monthly_ad_spend)
        self.schema_form.addRow("Setup Fee", self.setup_fee)
        self.schema_form.addRow("Ongoing Management", self.ongoing_management)
        self.schema_card.content_layout.addLayout(self.schema_form)

        left_col = QWidget()
        left_layout = QVBoxLayout(left_col)
        left_layout.addWidget(self.form)
        left_layout.addWidget(self.schema_card)

        split.addWidget(left_col)
        split.addWidget(self.results)
        split.addWidget(self.photo_panel)
        split.setSizes([500, 680, 360])

        action_card = Card()
        row = QHBoxLayout()
        self.status = QLabel("Live preview on")
        self.clear_btn = GhostButton("Clear")
        self.generate_btn = SecondaryButton("Generate Quote")
        self.export_btn = PrimaryButton("Export PDF")
        row.addWidget(self.status)
        row.addStretch(1)
        row.addWidget(self.clear_btn)
        row.addWidget(self.generate_btn)
        row.addWidget(self.export_btn)
        action_card.content_layout.addLayout(row)

        root.addWidget(control_card)
        root.addWidget(split, 1)
        root.addWidget(action_card)

        self._wire()
        self.refresh_industries()
        self._apply_saved_state()
        self._apply_industry_schema()

    def _wire(self) -> None:
        self.industry_combo.currentIndexChanged.connect(self._on_header_changed)
        self.region_combo.currentIndexChanged.connect(self._on_header_changed)
        self.urgency_combo.currentIndexChanged.connect(self._on_header_changed)
        self.tier_combo.currentIndexChanged.connect(self._on_header_changed)
        self.favorite_btn.clicked.connect(self._toggle_favorite)

        self.form.inputs_changed.connect(self._schedule_preview)
        self.photo_panel.images_changed.connect(self._images_changed)
        self.photo_panel.tags_changed.connect(self._tags_changed)
        self.photo_panel.refresh_tags_requested.connect(self._refresh_tags)

        for widget in [
            self.appliance_type,
            self.fault_type,
            self.callout_fee,
            self.labour_hours,
            self.parts_estimate,
            self.campaign_type,
            self.monthly_ad_spend,
            self.setup_fee,
            self.ongoing_management,
        ]:
            if hasattr(widget, "currentIndexChanged"):
                widget.currentIndexChanged.connect(self._schedule_preview)
            if hasattr(widget, "valueChanged"):
                widget.valueChanged.connect(self._schedule_preview)

        self.generate_btn.clicked.connect(self.generate_now)
        self.clear_btn.clicked.connect(self.clear_all)
        self.export_btn.clicked.connect(self.export_pdf)

    def refresh_industries(self) -> None:
        current = self.industry_combo.currentData()
        self.industry_combo.blockSignals(True)
        self.industry_combo.clear()
        favorites = self.settings.get("favorites_industries", [])
        entries = self.registry.list_industries()
        ordered = sorted(entries, key=lambda e: (0 if e["id"] in favorites else 1, e.get("group", "Other"), e["name"]))
        for entry in ordered:
            mark = "★ " if entry["id"] in favorites else ""
            self.industry_combo.addItem(f"[{entry.get('group','Other')}] {mark}{entry['name']}", entry["id"])
        idx = max(0, self.industry_combo.findData(current))
        self.industry_combo.setCurrentIndex(idx)
        self.industry_combo.blockSignals(False)
        self._sync_header_to_form()

    def _apply_saved_state(self) -> None:
        idx = self.industry_combo.findData(self.settings.get("last_industry_id", "cleaning"))
        self.industry_combo.setCurrentIndex(max(0, idx))
        self.region_combo.setCurrentText(self.settings.get("last_region", "DEFAULT"))
        self.urgency_combo.setCurrentText(self.settings.get("last_urgency", "standard"))
        self.tier_combo.setCurrentText(self.settings.get("tier", "FREE"))
        self._sync_header_to_form()

    def _toggle_favorite(self) -> None:
        current_id = self.industry_combo.currentData()
        favorites = list(self.settings.get("favorites_industries", []))
        if current_id in favorites:
            favorites.remove(current_id)
        else:
            favorites = [current_id] + [x for x in favorites if x != current_id]
            favorites = favorites[:10]
        self.settings["favorites_industries"] = favorites
        save_settings(self.settings)
        self.refresh_industries()

    def _industry(self) -> dict:
        return self.registry.get_industry(self.industry_combo.currentData())

    def _is_cleaning(self, industry: dict) -> bool:
        template = str(industry.get("template", "")).lower()
        name = str(industry.get("name", "")).lower()
        return template == "cleaning" or any(token in name for token in ["clean", "end of lease", "bond clean"])

    def _apply_industry_schema(self) -> None:
        industry = self._industry()
        name = str(industry.get("name", "")).lower()
        is_cleaning = self._is_cleaning(industry)
        is_appliance = "appliance" in name or "battery" in name
        is_ads = "ads" in name or "campaign" in name or "google" in name

        self.form.set_cleaning_mode(is_cleaning)

        rows = {
            self.appliance_type: is_appliance,
            self.fault_type: is_appliance,
            self.callout_fee: is_appliance,
            self.labour_hours: is_appliance,
            self.parts_estimate: is_appliance,
            self.campaign_type: is_ads,
            self.monthly_ad_spend: is_ads,
            self.setup_fee: is_ads,
            self.ongoing_management: is_ads,
        }
        visible_any = any(rows.values())
        self.schema_card.setVisible(visible_any)
        for widget, visible in rows.items():
            self.schema_form.setRowVisible(widget, visible)

        addon_source = industry.get("addons", {})
        addon_keys: list[str] = []
        if isinstance(addon_source, dict):
            addon_keys = sorted(addon_source.keys())
        elif isinstance(addon_source, list):
            for item in addon_source:
                if isinstance(item, dict):
                    key = str(item.get("key") or item.get("name") or item.get("id") or "").strip()
                    if key:
                        addon_keys.append(key)
                elif isinstance(item, str):
                    addon_keys.append(item)
            addon_keys = sorted(set(addon_keys))
        self.form.set_addons(addon_keys)

    def _on_header_changed(self) -> None:
        self._sync_header_to_form()
        self._apply_industry_schema()
        self._schedule_preview()

    def _sync_header_to_form(self) -> None:
        self.form.set_active_selections(
            industry_id=self.industry_combo.currentData(),
            industry_name=self.industry_combo.currentText(),
            region=self.region_combo.currentText(),
            urgency=self.urgency_combo.currentText(),
            tier=self.tier_combo.currentText(),
        )

    def _images_changed(self, paths: list[str]) -> None:
        self.form.set_images(paths)
        self._refresh_tags()

    def _refresh_tags(self) -> None:
        tags: list[str] = []
        for path in self.form.get_request_dict().get("image_paths", []):
            if path not in self.image_tag_cache:
                self.image_tag_cache[path] = analyze_images([path])
            tags.extend(self.image_tag_cache[path])
        self.photo_panel.set_detected_tags(sorted(set(tags)))

    def _tags_changed(self, tags: list[str]) -> None:
        self.confirmed_tags = tags
        self._schedule_preview()

    def _schedule_preview(self) -> None:
        self.preview_timer.start()

    def _apply_display_currency(self, quote: dict) -> dict:
        display = self.settings.get("currency", quote.get("currency", "AUD"))
        base = quote.get("currency", "AUD")
        if display == base:
            return quote
        rates = self.settings.get("currency_rates") or fetch_rates("AUD")
        conv = convert_amount(float(quote.get("total", 0)), base, display, rates)
        if conv is None:
            quote.setdefault("assumptions", []).append("Currency conversion unavailable (base)")
            return quote
        out = dict(quote)
        out["display_total"] = conv
        out["display_currency"] = display
        return out

    def _build_request(self) -> dict:
        req = self.form.get_request_dict()
        industry_name = str(self._industry().get("name", "")).lower()
        if "appliance" in industry_name or "battery" in industry_name:
            req["quantity_fields"].update(
                {
                    "appliance_type": self.appliance_type.currentText(),
                    "fault_type": self.fault_type.currentText(),
                    "callout_fee": self.callout_fee.value(),
                    "labour_hours": self.labour_hours.value(),
                    "parts_estimate": self.parts_estimate.value(),
                }
            )
        if "ads" in industry_name or "campaign" in industry_name or "google" in industry_name:
            req["quantity_fields"].update(
                {
                    "campaign_type": self.campaign_type.currentText(),
                    "monthly_ad_spend": self.monthly_ad_spend.value(),
                    "setup_fee": self.setup_fee.value(),
                    "ongoing_management": self.ongoing_management.value(),
                }
            )
        return req

    def _generate_live(self) -> None:
        req = self._build_request()
        self.current_quote = build_quote(req, confirmed_tags=self.confirmed_tags)
        self.current_quote = self._apply_display_currency(self.current_quote)
        self.results.set_quote_result(self.current_quote)
        self.photo_panel.set_applied_from_photos(self.current_quote.get("applied_modifiers", {}).get("tag_effects", []))
        self.status.setText(f"Live preview on • Updated {datetime.now().strftime('%H:%M:%S')}")

    def generate_now(self) -> None:
        self.preview_timer.stop()
        self._generate_live()
        if self.current_quote and "error" not in self.current_quote:
            industry = self._industry()
            quote_record = {
                "quote_id": self.current_quote.get("quote_id"),
                "industry_id": self.industry_combo.currentData(),
                "industry_name": industry.get("name"),
                "total": self.current_quote.get("total"),
                "currency": self.current_quote.get("currency"),
                "client_name": self.form.get_request_dict().get("client_name", ""),
                "scope_text": self.form.get_request_dict().get("scope_text", ""),
                "timestamp": datetime.utcnow().isoformat(),
                "breakdown": self.current_quote.get("breakdown", []),
                "quote": self.current_quote,
            }
            saved = save_quote(quote_record)
            self.quote_saved.emit(saved)

    def export_pdf(self) -> None:
        if not self.current_quote or "error" in self.current_quote:
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", str(Path.home() / "quote.pdf"), "PDF files (*.pdf)")
        if not path:
            return
        self.settings.update(
            {
                "last_industry_id": self.industry_combo.currentData(),
                "last_region": self.region_combo.currentText(),
                "last_urgency": self.urgency_combo.currentText(),
                "tier": self.tier_combo.currentText(),
            }
        )
        save_settings(self.settings)
        generate_quote_pdf(
            quote=self.current_quote,
            output_path=path,
            industry_name=self.industry_combo.currentText(),
            scope_text=self.form.get_request_dict().get("scope_text", ""),
            tier=self.tier_combo.currentText(),
            show_footer=bool(self.settings.get("pdf", {}).get("show_footer", self.tier_combo.currentText() == "FREE")),
            settings=self.settings,
        )

    def clear_all(self) -> None:
        self.form.clear_form()
        self.photo_panel.clear_panel()
        self.confirmed_tags = []
        self.current_quote = None
        self.results.set_quote_result({"currency": "AUD", "total": 0, "breakdown": [], "applied_modifiers": {}, "assumptions": []})
        self.status.setText("Live preview on")
