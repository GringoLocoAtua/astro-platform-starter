from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QSplitter,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from core.client_vault import get_client_history
from core.constants import DATA_DIR
from core.currency import convert_amount, fetch_rates
from core.industry_registry import IndustryRegistry
from core.quote_builder import analyze_images, build_quote
from core.settings_store import load_settings, save_settings
from export.pdf_generator import generate_quote_pdf
from ui.components import Card, GhostButton, PrimaryButton, SecondaryButton, ToastManager
from ui.i18n import i18n, tr
from ui.photo_panel import PhotoPanel
from ui.pricing_studio import PricingStudio
from ui.quote_form import QuoteForm
from ui.results_panel import ResultsPanel
from ui.settings_panel import SettingsPanel
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
        i18n.set_language(self.settings.get("language", "en"))
        self.current_quote: dict | None = None
        self.image_tag_cache: dict[str, list[str]] = {}
        self.confirmed_tags: list[str] = []
        self.preview_timer = QTimer(self)
        self.preview_timer.setSingleShot(True)
        self.preview_timer.setInterval(350)
        self.preview_timer.timeout.connect(self._generate_live)
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setWindowTitle(tr("app.title"))
        self.resize(1540, 900)

        root = QWidget()
        root.setObjectName("rootWindow")
        main = QVBoxLayout(root)
        main.setContentsMargins(16, 16, 16, 16)
        main.setSpacing(12)

        main.addWidget(self._build_top_bar())

        self.tabs = QTabWidget()
        self.dashboard_tab = self._build_dashboard_tab()
        self.quote_tab = self._build_quote_tab()
        self.library_tab = self._build_library_tab()
        self.pricing_studio = PricingStudio(self.registry)
        self.settings_panel = SettingsPanel()

        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.quote_tab, tr("tab.quote"))
        self.tabs.addTab(self.library_tab, "Library")
        self.tabs.addTab(self.pricing_studio, tr("tab.pricing"))
        self.tabs.addTab(self.settings_panel, tr("tab.settings"))

        main.addWidget(self.tabs, 1)
        main.addWidget(self._build_bottom_bar())

        self.setCentralWidget(root)
        self.toast = ToastManager(self)

        self._connect_signals()
        self._refresh_registry_dependent_ui()
        self._apply_saved_state()
        self._refresh_library()
        self._schedule_preview()

    def _build_top_bar(self) -> QWidget:
        bar = Card()
        row = QHBoxLayout()

        self.industry_search = QComboBox()
        self.industry_search.setEditable(True)
        self.region_combo = QComboBox()
        self.region_combo.addItems(["DEFAULT", "NSW", "VIC", "QLD", "NZ", "NZ-AUCKLAND"])
        self.urgency_combo = QComboBox()
        self.urgency_combo.addItems(["standard", "urgent", "same_day"])
        self.tier_combo = QComboBox()
        self.tier_combo.addItems(["FREE", "PRO"])
        self.lang_quick = QComboBox()
        self.lang_quick.addItems(["en", "es"])

        self.settings_btn = QToolButton()
        self.settings_btn.setText("⚙")

        row.addWidget(QLabel("SnapQuote"))
        row.addWidget(self.industry_search, 2)
        row.addWidget(self.region_combo)
        row.addWidget(self.urgency_combo)
        row.addWidget(self.tier_combo)
        row.addWidget(self.lang_quick)
        row.addWidget(self.settings_btn)

        bar.content_layout.addLayout(row)
        return bar

    def _build_dashboard_tab(self) -> QWidget:
        card = Card()
        card.content_layout.addWidget(QLabel("Dashboard"))
        btn_row = QHBoxLayout()
        self.new_quote_btn = PrimaryButton("New Quote")
        self.open_library_btn = SecondaryButton("Open Library")
        self.open_pricing_btn = SecondaryButton("Pricing Studio")
        self.open_settings_btn = GhostButton("Settings")
        btn_row.addWidget(self.new_quote_btn)
        btn_row.addWidget(self.open_library_btn)
        btn_row.addWidget(self.open_pricing_btn)
        btn_row.addWidget(self.open_settings_btn)
        card.content_layout.addLayout(btn_row)
        self.last_quote_label = QLabel("Last quote: none")
        self.last_quote_label.setObjectName("subtitle")
        card.content_layout.addWidget(self.last_quote_label)
        w = QWidget()
        l = QVBoxLayout(w)
        l.addWidget(card)
        l.addStretch(1)
        return w

    def _build_quote_tab(self) -> QWidget:
        panel = QWidget()
        layout = QVBoxLayout(panel)
        split = QSplitter(Qt.Orientation.Horizontal)
        self.form = QuoteForm(self.registry.list_industries())
        self.results = ResultsPanel()
        self.photo_panel = PhotoPanel()
        split.addWidget(self.form)
        split.addWidget(self.results)
        split.addWidget(self.photo_panel)
        split.setSizes([420, 680, 360])
        layout.addWidget(split)
        return panel

    def _build_library_tab(self) -> QWidget:
        w = QWidget()
        layout = QVBoxLayout(w)
        card = Card()
        card.content_layout.addWidget(QLabel("Library"))
        self.library_list = QListWidget()
        actions = QHBoxLayout()
        self.open_item_btn = SecondaryButton("Open Selected")
        self.open_folder_btn = GhostButton("Open Data Folder")
        actions.addWidget(self.open_item_btn)
        actions.addWidget(self.open_folder_btn)
        card.content_layout.addWidget(self.library_list)
        card.content_layout.addLayout(actions)
        layout.addWidget(card)
        return w

    def _build_bottom_bar(self) -> QWidget:
        bar = Card()
        row = QHBoxLayout()
        self.status_label = QLabel("Live preview on")
        self.status_label.setObjectName("subtitle")
        row.addWidget(self.status_label)
        row.addStretch(1)
        self.clear_btn = GhostButton(tr("btn.clear"))
        self.generate_btn = SecondaryButton(tr("btn.generate"))
        self.export_btn = PrimaryButton(tr("btn.export"))
        row.addWidget(self.clear_btn)
        row.addWidget(self.generate_btn)
        row.addWidget(self.export_btn)
        bar.content_layout.addLayout(row)
        return bar

    def _connect_signals(self) -> None:
        self.industry_search.currentIndexChanged.connect(self._on_header_inputs_changed)
        self.region_combo.currentIndexChanged.connect(self._on_header_inputs_changed)
        self.urgency_combo.currentIndexChanged.connect(self._on_header_inputs_changed)
        self.tier_combo.currentIndexChanged.connect(self._on_header_inputs_changed)
        self.lang_quick.currentTextChanged.connect(self._language_switched)
        self.settings_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(4))

        self.form.inputs_changed.connect(self._schedule_preview)
        self.photo_panel.images_changed.connect(self._images_changed)
        self.photo_panel.tags_changed.connect(self._tags_changed)
        self.photo_panel.refresh_tags_requested.connect(self._refresh_tags)

        self.generate_btn.clicked.connect(self._generate_manual)
        self.export_btn.clicked.connect(self._export_pdf)
        self.clear_btn.clicked.connect(self._clear)

        self.pricing_studio.active_industry_changed.connect(self._refresh_registry_dependent_ui)
        self.settings_panel.settings_changed.connect(self._settings_updated)
        self.settings_panel.logout_requested.connect(self.close)

        self.new_quote_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(1))
        self.open_library_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(2))
        self.open_pricing_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(3))
        self.open_settings_btn.clicked.connect(lambda: self.tabs.setCurrentIndex(4))
        self.open_folder_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(DATA_DIR))))
        self.open_item_btn.clicked.connect(self._open_library_selected)

    def _open_library_selected(self) -> None:
        item = self.library_list.currentItem()
        if not item:
            return
        path = Path(item.data(Qt.ItemDataRole.UserRole))
        if path.exists():
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))

    def _refresh_library(self) -> None:
        self.library_list.clear()
        for pdf in sorted(DATA_DIR.glob("*.pdf")):
            from PyQt6.QtWidgets import QListWidgetItem

            it = QListWidgetItem(f"PDF: {pdf.name}")
            it.setData(Qt.ItemDataRole.UserRole, str(pdf))
            self.library_list.addItem(it)
        for client in ["default", "sample"]:
            history = get_client_history(client)
            if history:
                from PyQt6.QtWidgets import QListWidgetItem

                it = QListWidgetItem(f"Client Quotes: {client} ({len(history)})")
                it.setData(Qt.ItemDataRole.UserRole, str(DATA_DIR))
                self.library_list.addItem(it)

    def _language_switched(self, language: str) -> None:
        i18n.set_language(language)
        self.settings["language"] = language
        save_settings(self.settings)

    def _settings_updated(self, settings: dict) -> None:
        self.settings = settings
        self.region_combo.setCurrentText(self.settings.get("last_region", "DEFAULT"))
        self.urgency_combo.setCurrentText(self.settings.get("last_urgency", "standard"))
        self.tier_combo.setCurrentText(self.settings.get("tier", "FREE"))

    def _apply_saved_state(self) -> None:
        idx = self.industry_search.findData(self.settings.get("last_industry_id", "cleaning"))
        self.industry_search.setCurrentIndex(max(0, idx))
        self.region_combo.setCurrentText(self.settings.get("last_region", "DEFAULT"))
        self.urgency_combo.setCurrentText(self.settings.get("last_urgency", "standard"))
        self.tier_combo.setCurrentText(self.settings.get("tier", "FREE"))
        self.lang_quick.setCurrentText(self.settings.get("language", "en"))
        self._sync_header_to_form()

    def _refresh_registry_dependent_ui(self) -> None:
        entries = self.registry.list_industries()
        current_id = self.industry_search.currentData()
        self.industry_search.blockSignals(True)
        self.industry_search.clear()
        favorites = self.settings.get("favorites_industries", [])
        ordered = sorted(entries, key=lambda e: (0 if e["id"] in favorites else 1, e.get("group", "Other"), e["name"]))
        for entry in ordered:
            label = f"★ {entry['name']}" if entry["id"] in favorites else entry["name"]
            self.industry_search.addItem(f"[{entry.get('group','Other')}] {label}", entry["id"])
        idx = max(0, self.industry_search.findData(current_id))
        self.industry_search.setCurrentIndex(idx)
        self.industry_search.blockSignals(False)
        self._sync_header_to_form()
        self._update_addons_for_industry()

    def _is_cleaning_industry(self, industry: dict) -> bool:
        template = str(industry.get("template", "")).lower()
        name = str(industry.get("name", "")).lower()
        return template == "cleaning" or any(token in name for token in ["clean", "end of lease", "bond clean"])

    def _addons_to_keys(self, addons) -> list[str]:
        if isinstance(addons, dict):
            return sorted(addons.keys())
        if isinstance(addons, list):
            keys: list[str] = []
            for item in addons:
                if isinstance(item, dict):
                    key = str(item.get("key") or item.get("name") or item.get("id") or "").strip()
                    if key:
                        keys.append(key)
                elif isinstance(item, str):
                    keys.append(item)
            return sorted(set(keys))
        return []

    def _on_header_inputs_changed(self) -> None:
        self._sync_header_to_form()
        self._update_addons_for_industry()
        self._schedule_preview()

    def _sync_header_to_form(self) -> None:
        self.form.set_active_selections(
            industry_id=self.industry_search.currentData(),
            industry_name=self.industry_search.currentText(),
            region=self.region_combo.currentText(),
            urgency=self.urgency_combo.currentText(),
            tier=self.tier_combo.currentText(),
        )

    def _update_addons_for_industry(self) -> None:
        industry_id = self.industry_search.currentData()
        if not industry_id:
            return
        industry = self.registry.get_industry(industry_id)
        self.form.set_addons(self._addons_to_keys(industry.get("addons", {})))
        self.form.set_cleaning_mode(self._is_cleaning_industry(industry))

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
        quote = dict(quote)
        quote["display_total"] = conv
        quote["display_currency"] = display
        return quote

    def _generate_live(self) -> None:
        req = self.form.get_request_dict()
        self.current_quote = build_quote(req, confirmed_tags=self.confirmed_tags)
        self.current_quote = self._apply_display_currency(self.current_quote)
        self.results.set_quote_result(self.current_quote)
        self.photo_panel.set_applied_from_photos(self.current_quote.get("applied_modifiers", {}).get("tag_effects", []))
        self.status_label.setText(f"Live preview on • Updated {datetime.now().strftime('%H:%M:%S')}")
        if self.current_quote and "error" not in self.current_quote:
            self.last_quote_label.setText(f"Last quote total: {self.current_quote.get('currency','AUD')} {self.current_quote.get('total',0):.2f}")

    def _generate_manual(self) -> None:
        self.preview_timer.stop()
        self._generate_live()
        self.toast.show_toast("Quote generated" if self.current_quote and "error" not in self.current_quote else "Quote failed")

    def _export_pdf(self) -> None:
        if not self.current_quote or "error" in self.current_quote:
            self.toast.show_toast("Generate a quote first")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", str(Path.home() / "quote.pdf"), "PDF files (*.pdf)")
        if not path:
            return
        self.settings.update(
            {
                "last_industry_id": self.industry_search.currentData(),
                "last_region": self.region_combo.currentText(),
                "last_urgency": self.urgency_combo.currentText(),
                "tier": self.tier_combo.currentText(),
            }
        )
        save_settings(self.settings)
        generate_quote_pdf(
            quote=self.current_quote,
            output_path=path,
            industry_name=self.industry_search.currentText(),
            scope_text=self.form.get_request_dict().get("scope_text", ""),
            tier=self.tier_combo.currentText(),
            show_footer=bool(self.settings.get("pdf", {}).get("show_footer", self.tier_combo.currentText() == "FREE")),
            settings=self.settings,
        )
        self.toast.show_toast("PDF exported")
        self._refresh_library()

    def _clear(self) -> None:
        self.form.clear_form()
        self.photo_panel.clear_panel()
        self.confirmed_tags = []
        self.current_quote = None
        self.results.set_quote_result({"currency": "AUD", "total": 0, "breakdown": [], "applied_modifiers": {}, "assumptions": []})
        self.status_label.setText("Live preview on")
        self.toast.show_toast("Cleared")
