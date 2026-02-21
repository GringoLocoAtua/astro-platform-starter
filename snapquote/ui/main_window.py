from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from core.industry_registry import IndustryRegistry
from core.quote_builder import analyze_images, build_quote
from core.settings_store import load_settings, save_settings
from export.pdf_generator import generate_quote_pdf
from ui.photo_panel import PhotoPanel
from ui.pricing_studio import PricingStudio
from ui.quote_form import QuoteForm
from ui.results_panel import ResultsPanel


DARK_THEME = """
QWidget { background-color: #151820; color: #E6EAF2; font-size: 13px; }
QPushButton { background: #334155; border: 1px solid #475569; padding: 6px 10px; border-radius: 6px; }
QLineEdit, QTextEdit, QComboBox, QListWidget, QSpinBox, QTableWidget { background: #0f172a; border: 1px solid #334155; border-radius: 6px; }
QGroupBox { border: 1px solid #334155; margin-top: 8px; }
"""


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
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
        self.setWindowTitle("SnapQuote v2.1")
        self.resize(1360, 780)
        self.setStyleSheet(DARK_THEME)

        tabs = QTabWidget()
        self.setCentralWidget(tabs)

        tabs.addTab(self._build_quote_tab(), "Quote")
        self.pricing_studio = PricingStudio(self.registry)
        self.pricing_studio.active_industry_changed.connect(self._refresh_registry_dependent_ui)
        tabs.addTab(self.pricing_studio, "Pricing Studio")
        tabs.addTab(self._build_settings_tab(), "Settings")

        self._refresh_registry_dependent_ui()
        self._apply_saved_state()

    def _build_quote_tab(self) -> QWidget:
        panel = QWidget()
        root = QVBoxLayout(panel)
        split = QHBoxLayout()

        left = QVBoxLayout()
        self.form = QuoteForm(self.registry.list_industries())
        self.photo_panel = PhotoPanel()
        left.addWidget(self.form)
        left.addWidget(self.photo_panel)

        self.results = ResultsPanel()
        split.addLayout(left, 3)
        split.addWidget(self.results, 2)

        actions = QHBoxLayout()
        self.generate_btn = QPushButton("Generate Quote")
        self.export_btn = QPushButton("Export PDF")
        self.clear_btn = QPushButton("Clear")
        actions.addWidget(self.generate_btn)
        actions.addWidget(self.export_btn)
        actions.addWidget(self.clear_btn)

        root.addLayout(split)
        root.addLayout(actions)

        self.form.quote_inputs_changed.connect(self._schedule_preview)
        self.form.industry.currentIndexChanged.connect(self._industry_changed)
        self.photo_panel.images_changed.connect(self._images_changed)
        self.photo_panel.tags_changed.connect(self._tags_changed)
        self.photo_panel.refresh_tags_requested.connect(self._refresh_tags)
        self.generate_btn.clicked.connect(self._generate_manual)
        self.export_btn.clicked.connect(self._export_pdf)
        self.clear_btn.clicked.connect(self._clear)
        return panel

    def _build_settings_tab(self) -> QWidget:
        panel = QWidget()
        form = QFormLayout(panel)
        self.business_name = QLineEdit(self.settings.get("branding", {}).get("business_name", ""))
        self.business_phone = QLineEdit(self.settings.get("branding", {}).get("phone", ""))
        self.business_email = QLineEdit(self.settings.get("branding", {}).get("email", ""))
        self.logo_path = QLineEdit(self.settings.get("branding", {}).get("logo_path", ""))
        self.logo_pick = QPushButton("Browse")
        self.pro_footer_enabled = QCheckBox("Enable PRO footer")
        self.pro_footer_enabled.setChecked(bool(self.settings.get("pro_footer_enabled", False)))
        self.save_settings_btn = QPushButton("Save Settings")

        logo_line = QHBoxLayout()
        logo_line.addWidget(self.logo_path)
        logo_line.addWidget(self.logo_pick)

        form.addRow("Business Name", self.business_name)
        form.addRow("Phone", self.business_phone)
        form.addRow("Email", self.business_email)
        form.addRow("Logo Path", logo_line)
        form.addRow(self.pro_footer_enabled)
        form.addRow(self.save_settings_btn)

        self.logo_pick.clicked.connect(self._pick_logo)
        self.save_settings_btn.clicked.connect(self._save_settings)
        return panel

    def _pick_logo(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Select Logo", str(Path.home()))
        if path:
            self.logo_path.setText(path)

    def _save_settings(self) -> None:
        self.settings.update(
            {
                "last_selected_industry": self.form.industry.currentData(),
                "last_region": self.form.region.currentText(),
                "last_urgency": self.form.urgency.currentText(),
                "last_tier": self.form.tier.currentText(),
                "pro_footer_enabled": self.pro_footer_enabled.isChecked(),
                "branding": {
                    "business_name": self.business_name.text().strip(),
                    "phone": self.business_phone.text().strip(),
                    "email": self.business_email.text().strip(),
                    "logo_path": self.logo_path.text().strip(),
                },
            }
        )
        save_settings(self.settings)
        QMessageBox.information(self, "Saved", "Settings saved.")

    def _apply_saved_state(self) -> None:
        industry = self.settings.get("last_selected_industry")
        idx = self.form.industry.findData(industry)
        if idx >= 0:
            self.form.industry.setCurrentIndex(idx)
        self.form.region.setCurrentText(self.settings.get("last_region", "DEFAULT"))
        self.form.urgency.setCurrentText(self.settings.get("last_urgency", "standard"))
        self.form.tier.setCurrentText(self.settings.get("last_tier", "FREE"))

    def _refresh_registry_dependent_ui(self) -> None:
        self.form.refresh_industries(self.registry.list_industries())
        self._industry_changed(0)

    def _industry_changed(self, _: int) -> None:
        industry_id = self.form.industry.currentData()
        if not industry_id:
            return
        industry = self.registry.get_industry(industry_id)
        self.form.set_addons(sorted(industry.get("addons", {}).keys()))
        self._schedule_preview()

    def _images_changed(self, paths: list[str]) -> None:
        self.form.set_images(paths)
        self._refresh_tags()

    def _refresh_tags(self) -> None:
        paths = self.form.values().get("image_paths", [])
        tags: list[str] = []
        for path in paths:
            if path not in self.image_tag_cache:
                self.image_tag_cache[path] = analyze_images([path])
            tags.extend(self.image_tag_cache.get(path, []))
        self.photo_panel.set_detected_tags(sorted(set(tags)))

    def _tags_changed(self, tags: list[str]) -> None:
        self.confirmed_tags = tags
        self._schedule_preview()

    def _schedule_preview(self) -> None:
        self.preview_timer.start()

    def _generate_live(self) -> None:
        self.current_quote = build_quote(self.form.values(), confirmed_tags=self.confirmed_tags)
        self.results.show_quote(self.current_quote)

    def _generate_manual(self) -> None:
        self.preview_timer.stop()
        self._generate_live()

    def _export_pdf(self) -> None:
        if not self.current_quote or "error" in self.current_quote:
            QMessageBox.warning(self, "No Quote", "Generate a quote first.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", str(Path.home() / "quote.pdf"), "PDF files (*.pdf)")
        if not path:
            return
        self._save_settings()
        output = generate_quote_pdf(
            quote=self.current_quote,
            output_path=path,
            industry_name=self.form.industry.currentText(),
            scope_text=self.form.values().get("scope_text", ""),
            tier=self.form.tier.currentText(),
            show_footer=bool(self.settings.get("pro_footer_enabled", False)),
            settings=self.settings,
        )
        QMessageBox.information(self, "Exported", f"Saved PDF to {output}")

    def _clear(self) -> None:
        self.form.clear_form()
        self.photo_panel.clear_panel()
        self.confirmed_tags = []
        self.current_quote = None
        self.results.show_quote({"currency": "AUD", "total": 0, "breakdown": [], "applied_modifiers": {}, "assumptions": []})
