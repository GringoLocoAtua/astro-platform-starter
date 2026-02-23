from __future__ import annotations

from PyQt6.QtWidgets import QMainWindow, QTabWidget

from core.industry_registry import IndustryRegistry
from ui.tabs.dashboard_tab import DashboardTab
from ui.tabs.library_tab import LibraryTab
from ui.tabs.new_quote_tab import NewQuoteTab
from ui.tabs.profile_tab import ProfileTab
from ui.tabs.settings_tab import SettingsTab
from ui.pricing_studio import PricingStudio


class AppShell(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("SnapQuote")
        self.resize(1580, 920)

        self.registry = IndustryRegistry()
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.dashboard_tab = DashboardTab()
        self.new_quote_tab = NewQuoteTab(self.registry)
        self.library_tab = LibraryTab()
        self.pricing_tab = PricingStudio(self.registry)
        self.settings_tab = SettingsTab()
        self.profile_tab = ProfileTab()

        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.addTab(self.new_quote_tab, "New Quote")
        self.tabs.addTab(self.library_tab, "Quote Library")
        self.tabs.addTab(self.pricing_tab, "Pricing Studio")
        self.tabs.addTab(self.settings_tab, "Settings")
        self.tabs.addTab(self.profile_tab, "Profile / Login")

        self.tabs.setCurrentIndex(0)

        self.dashboard_tab.open_new_quote.connect(lambda: self.tabs.setCurrentWidget(self.new_quote_tab))
        self.dashboard_tab.open_library.connect(lambda: self.tabs.setCurrentWidget(self.library_tab))
        self.dashboard_tab.open_pricing.connect(lambda: self.tabs.setCurrentWidget(self.pricing_tab))
        self.dashboard_tab.open_settings.connect(lambda: self.tabs.setCurrentWidget(self.settings_tab))
        self.dashboard_tab.open_profile.connect(lambda: self.tabs.setCurrentWidget(self.profile_tab))

        self.new_quote_tab.quote_saved.connect(self._on_quote_saved)
        self.pricing_tab.active_industry_changed.connect(self._refresh_after_pricing_change)

    def _on_quote_saved(self, quote: dict) -> None:
        summary = f"Last quote: {quote.get('industry_name','')} - {quote.get('currency','AUD')} {quote.get('total',0)}"
        self.dashboard_tab.set_last_quote_summary(summary)
        self.library_tab.refresh()

    def _refresh_after_pricing_change(self) -> None:
        self.registry.reload()
        self.new_quote_tab.refresh_industries()
