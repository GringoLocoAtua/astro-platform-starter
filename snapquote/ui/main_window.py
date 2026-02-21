from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSplitter,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from core.industry_registry import IndustryRegistry
from core.quote_builder import analyze_images, build_quote
from core.settings_store import load_settings, save_settings
from export.pdf_generator import generate_quote_pdf
from ui.components import Card, GhostButton, PrimaryButton, SecondaryButton, SectionHeader, ToastManager
from ui.photo_panel import PhotoPanel
from ui.pricing_studio import PricingStudio
from ui.quote_form import QuoteForm
from ui.results_panel import ResultsPanel
from ui.theme import apply_theme


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        from PyQt6.QtWidgets import QApplication

        app = QApplication.instance()
        if app is not None:
            apply_theme(app)

        self.registry = IndustryRegistry()
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
        self.setWindowTitle("SnapQuote")
        self.resize(1540, 900)

        root = QWidget()
        root.setObjectName("rootWindow")
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(16, 16, 16, 16)
        root_layout.setSpacing(12)

        root_layout.addWidget(self._build_top_bar())

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.form = QuoteForm(self.registry.list_industries())
        self.results = ResultsPanel()
        self.photo_panel = PhotoPanel()

        splitter.addWidget(self.form)
        splitter.addWidget(self.results)
        splitter.addWidget(self.photo_panel)
        splitter.setSizes([420, 680, 360])
        root_layout.addWidget(splitter, 1)

        root_layout.addWidget(self._build_bottom_bar())

        self.setCentralWidget(root)
        self.toast = ToastManager(self)

        self._build_settings_dialog()
        self._connect_signals()
        self._refresh_registry_dependent_ui()
        self._apply_saved_state()
        self._schedule_preview()

    def _build_top_bar(self) -> QWidget:
        bar = Card()
        row = QHBoxLayout()

        logo = QLabel("◉")
        logo.setStyleSheet("font-size:20px; color:#9ab6ff;")
        title = QLabel("SnapQuote")
        title.setObjectName("title")
        badge = QLabel("v2.1")
        badge.setObjectName("badge")

        left = QHBoxLayout()
        left.addWidget(logo)
        left.addWidget(title)
        left.addWidget(badge)
        left.addStretch(1)

        self.industry_combo = QComboBox()
        self.region_combo = QComboBox()
        self.urgency_combo = QComboBox()
        self.tier_combo = QComboBox()

        for entry in self.registry.list_industries():
            self.industry_combo.addItem(entry["name"], entry["id"])
        self.region_combo.addItems(["DEFAULT", "NSW", "VIC", "QLD", "NZ", "NZ-AUCKLAND"])
        self.urgency_combo.addItems(["standard", "urgent", "same_day"])
        self.tier_combo.addItems(["FREE", "PRO"])

        center = QHBoxLayout()
        center.addWidget(self.industry_combo)
        center.addWidget(self.region_combo)
        center.addWidget(self.urgency_combo)

        self.settings_btn = QToolButton()
        self.settings_btn.setText("⚙")
        self.settings_btn.setToolTip("Settings & Pricing Studio")

        right = QHBoxLayout()
        right.addWidget(self.tier_combo)
        right.addWidget(self.settings_btn)

        row.addLayout(left, 2)
        row.addLayout(center, 3)
        row.addLayout(right, 1)

        bar.content_layout.addLayout(row)
        return bar

    def _build_bottom_bar(self) -> QWidget:
        bar = Card()
        row = QHBoxLayout()
        self.status_label = QLabel("Live preview on")
        self.status_label.setObjectName("subtitle")
        row.addWidget(self.status_label)
        row.addStretch(1)

        self.export_btn = PrimaryButton("Export PDF")
        self.generate_btn = SecondaryButton("Generate Quote")
        self.clear_btn = GhostButton("Clear")
        row.addWidget(self.clear_btn)
        row.addWidget(self.generate_btn)
        row.addWidget(self.export_btn)
        bar.content_layout.addLayout(row)
        return bar

    def _build_settings_dialog(self) -> None:
        self.settings_dialog = QDialog(self)
        self.settings_dialog.setWindowTitle("Workspace")
        self.settings_dialog.resize(980, 700)
        layout = QVBoxLayout(self.settings_dialog)
        tabs = QTabWidget()

        settings_page = QWidget()
        settings_form = QFormLayout(settings_page)
        self.business_name = QLineEdit(self.settings.get("branding", {}).get("business_name", ""))
        self.business_phone = QLineEdit(self.settings.get("branding", {}).get("phone", ""))
        self.business_email = QLineEdit(self.settings.get("branding", {}).get("email", ""))
        self.logo_path = QLineEdit(self.settings.get("branding", {}).get("logo_path", ""))
        self.logo_pick = QPushButton("Browse")
        self.pro_footer_toggle = QComboBox(); self.pro_footer_toggle.addItems(["OFF", "ON"])
        self.pro_footer_toggle.setCurrentText("ON" if self.settings.get("pro_footer_enabled", False) else "OFF")
        logo_row = QHBoxLayout(); logo_row.addWidget(self.logo_path); logo_row.addWidget(self.logo_pick)
        settings_form.addRow("Business Name", self.business_name)
        settings_form.addRow("Phone", self.business_phone)
        settings_form.addRow("Email", self.business_email)
        settings_form.addRow("Logo Path", logo_row)
        settings_form.addRow("PRO Footer", self.pro_footer_toggle)
        self.save_settings_btn = SecondaryButton("Save Settings")
        settings_form.addRow(self.save_settings_btn)

        self.pricing_studio = PricingStudio(self.registry)
        self.pricing_studio.active_industry_changed.connect(self._refresh_registry_dependent_ui)

        tabs.addTab(settings_page, "Settings")
        tabs.addTab(self.pricing_studio, "Pricing Studio")
        layout.addWidget(tabs)

    def _connect_signals(self) -> None:
        self.industry_combo.currentIndexChanged.connect(self._on_header_inputs_changed)
        self.region_combo.currentIndexChanged.connect(self._on_header_inputs_changed)
        self.urgency_combo.currentIndexChanged.connect(self._on_header_inputs_changed)
        self.tier_combo.currentIndexChanged.connect(self._on_header_inputs_changed)

        self.form.inputs_changed.connect(self._schedule_preview)
        self.photo_panel.images_changed.connect(self._images_changed)
        self.photo_panel.tags_changed.connect(self._tags_changed)
        self.photo_panel.refresh_tags_requested.connect(self._refresh_tags)

        self.generate_btn.clicked.connect(self._generate_manual)
        self.export_btn.clicked.connect(self._export_pdf)
        self.clear_btn.clicked.connect(self._clear)

        self.settings_btn.clicked.connect(self.settings_dialog.show)
        self.logo_pick.clicked.connect(self._pick_logo)
        self.save_settings_btn.clicked.connect(self._save_settings)

    def _apply_saved_state(self) -> None:
        idx = self.industry_combo.findData(self.settings.get("last_selected_industry", "cleaning"))
        self.industry_combo.setCurrentIndex(max(0, idx))
        self.region_combo.setCurrentText(self.settings.get("last_region", "DEFAULT"))
        self.urgency_combo.setCurrentText(self.settings.get("last_urgency", "standard"))
        self.tier_combo.setCurrentText(self.settings.get("last_tier", "FREE"))
        self._sync_header_to_form()

    def _refresh_registry_dependent_ui(self) -> None:
        entries = self.registry.list_industries()
        current_id = self.industry_combo.currentData()
        self.industry_combo.blockSignals(True)
        self.industry_combo.clear()
        for entry in entries:
            self.industry_combo.addItem(entry["name"], entry["id"])
        idx = max(0, self.industry_combo.findData(current_id))
        self.industry_combo.setCurrentIndex(idx)
        self.industry_combo.blockSignals(False)
        self._sync_header_to_form()
        self._update_addons_for_industry()

    def _on_header_inputs_changed(self) -> None:
        self._sync_header_to_form()
        self._update_addons_for_industry()
        self._schedule_preview()

    def _sync_header_to_form(self) -> None:
        self.form.set_active_selections(
            industry_id=self.industry_combo.currentData(),
            industry_name=self.industry_combo.currentText(),
            region=self.region_combo.currentText(),
            urgency=self.urgency_combo.currentText(),
            tier=self.tier_combo.currentText(),
        )

    def _update_addons_for_industry(self) -> None:
        industry_id = self.industry_combo.currentData()
        if not industry_id:
            return
        industry = self.registry.get_industry(industry_id)
        self.form.set_addons(sorted(industry.get("addons", {}).keys()))

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

    def _generate_live(self) -> None:
        req = self.form.get_request_dict()
        self.current_quote = build_quote(req, confirmed_tags=self.confirmed_tags)
        self.results.set_quote_result(self.current_quote)
        self.photo_panel.set_applied_from_photos(self.current_quote.get("applied_modifiers", {}).get("tag_effects", []))
        self.status_label.setText(f"Live preview on • Updated {datetime.now().strftime('%H:%M:%S')}")

    def _generate_manual(self) -> None:
        self.preview_timer.stop()
        self._generate_live()
        if self.current_quote and "error" not in self.current_quote:
            self.toast.show_toast("Quote generated")
        else:
            self.toast.show_toast("Quote failed")

    def _pick_logo(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select Logo", str(Path.home()))
        if path:
            self.logo_path.setText(path)

    def _save_settings(self) -> None:
        self.settings.update(
            {
                "last_selected_industry": self.industry_combo.currentData(),
                "last_region": self.region_combo.currentText(),
                "last_urgency": self.urgency_combo.currentText(),
                "last_tier": self.tier_combo.currentText(),
                "pro_footer_enabled": self.pro_footer_toggle.currentText() == "ON",
                "branding": {
                    "business_name": self.business_name.text().strip(),
                    "phone": self.business_phone.text().strip(),
                    "email": self.business_email.text().strip(),
                    "logo_path": self.logo_path.text().strip(),
                },
            }
        )
        save_settings(self.settings)
        self.toast.show_toast("Settings saved")

    def _export_pdf(self) -> None:
        if not self.current_quote or "error" in self.current_quote:
            self.toast.show_toast("Generate a quote first")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", str(Path.home() / "quote.pdf"), "PDF files (*.pdf)")
        if not path:
            return
        self._save_settings()
        generate_quote_pdf(
            quote=self.current_quote,
            output_path=path,
            industry_name=self.industry_combo.currentText(),
            scope_text=self.form.get_request_dict().get("scope_text", ""),
            tier=self.tier_combo.currentText(),
            show_footer=bool(self.settings.get("pro_footer_enabled", False)),
            settings=self.settings,
        )
        self.toast.show_toast("PDF exported")

    def _clear(self) -> None:
        self.form.clear_form()
        self.photo_panel.clear_panel()
        self.confirmed_tags = []
        self.current_quote = None
        self.results.set_quote_result({"currency": "AUD", "total": 0, "breakdown": [], "applied_modifiers": {}, "assumptions": []})
        self.status_label.setText("Live preview on")
        self.toast.show_toast("Cleared")
