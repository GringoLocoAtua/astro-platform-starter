from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QCheckBox, QComboBox, QFormLayout, QHBoxLayout, QLineEdit, QPushButton, QSpinBox, QVBoxLayout, QWidget

from core.auth import clear_session, load_session
from core.settings_store import load_settings, save_settings
from ui.components import Card, SectionHeader
from ui.i18n import i18n, tr


class SettingsPanel(QWidget):
    settings_changed = pyqtSignal(dict)
    logout_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.settings = load_settings()
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        self.profile_card = Card(); self.profile_card.content_layout.addWidget(SectionHeader("Profile"))
        session = load_session()
        self.current_user = QLineEdit(session.get("username", "guest")); self.current_user.setReadOnly(True)
        self.logout_btn = QPushButton(tr("btn.logout"))
        pform = QFormLayout(); pform.addRow("User", self.current_user); pform.addRow(self.logout_btn)
        self.profile_card.content_layout.addLayout(pform)

        self.app_card = Card(); self.app_card.content_layout.addWidget(SectionHeader("App"))
        self.theme = QComboBox(); self.theme.addItems(["dark", "light"])
        self.language = QComboBox(); self.language.addItems(["en", "es"])
        self.currency = QComboBox(); self.currency.addItems(["AUD", "NZD", "USD", "EUR", "GBP", "CLP"])
        aform = QFormLayout(); aform.addRow(tr("settings.theme"), self.theme); aform.addRow(tr("settings.language"), self.language); aform.addRow(tr("settings.currency"), self.currency)
        self.app_card.content_layout.addLayout(aform)

        self.defaults_card = Card(); self.defaults_card.content_layout.addWidget(SectionHeader("Quote Defaults"))
        self.default_region = QLineEdit(); self.default_urgency = QComboBox(); self.default_urgency.addItems(["standard", "urgent", "same_day"])
        self.default_tier = QComboBox(); self.default_tier.addItems(["FREE", "PRO"])
        dform = QFormLayout(); dform.addRow(tr("field.region"), self.default_region); dform.addRow(tr("field.urgency"), self.default_urgency); dform.addRow(tr("field.tier"), self.default_tier)
        self.defaults_card.content_layout.addLayout(dform)

        self.pdf_card = Card(); self.pdf_card.content_layout.addWidget(SectionHeader("PDF / Tiering"))
        self.pdf_watermark = QCheckBox(tr("settings.watermark")); self.pdf_footer = QCheckBox(tr("settings.footer")); self.footer_text = QLineEdit()
        pfform = QFormLayout(); pfform.addRow(self.pdf_watermark); pfform.addRow(self.pdf_footer); pfform.addRow("Footer Text", self.footer_text)
        self.pdf_card.content_layout.addLayout(pfform)

        self.branding_card = Card(); self.branding_card.content_layout.addWidget(SectionHeader(tr("settings.branding")))
        self.business_name = QLineEdit(); self.business_email = QLineEdit(); self.business_phone = QLineEdit(); self.logo_path = QLineEdit(); self.logo_pick = QPushButton("Browse")
        brow = QHBoxLayout(); brow.addWidget(self.logo_path); brow.addWidget(self.logo_pick)
        bform = QFormLayout(); bform.addRow("Business", self.business_name); bform.addRow("Email", self.business_email); bform.addRow("Phone", self.business_phone); bform.addRow("Logo", brow)
        self.branding_card.content_layout.addLayout(bform)

        self.security_card = Card(); self.security_card.content_layout.addWidget(SectionHeader("Security"))
        self.require_login = QCheckBox(tr("settings.require_login")); self.auto_lock = QSpinBox(); self.auto_lock.setRange(0, 240)
        sform = QFormLayout(); sform.addRow(self.require_login); sform.addRow("Auto Lock (min)", self.auto_lock)
        self.security_card.content_layout.addLayout(sform)

        self.save_btn = QPushButton("Save Settings")
        self.save_btn.setObjectName("primary")

        for c in [self.profile_card, self.app_card, self.defaults_card, self.pdf_card, self.branding_card, self.security_card]:
            root.addWidget(c)
        root.addWidget(self.save_btn)
        root.addStretch(1)

        self.save_btn.clicked.connect(self._save)
        self.logout_btn.clicked.connect(self._logout)
        self.logo_pick.clicked.connect(self._pick_logo)
        self.language.currentTextChanged.connect(self._lang_changed)
        self._load()

    def _pick_logo(self) -> None:
        from PyQt6.QtWidgets import QFileDialog

        path, _ = QFileDialog.getOpenFileName(self, "Select logo")
        if path:
            self.logo_path.setText(path)

    def _lang_changed(self, lang: str) -> None:
        i18n.set_language(lang)

    def _load(self) -> None:
        s = self.settings
        self.theme.setCurrentText(s.get("theme", "dark"))
        self.language.setCurrentText(s.get("language", "en"))
        self.currency.setCurrentText(s.get("currency", "AUD"))
        self.default_region.setText(s.get("last_region", "DEFAULT"))
        self.default_urgency.setCurrentText(s.get("last_urgency", "standard"))
        self.default_tier.setCurrentText(s.get("tier", "FREE"))
        self.pdf_watermark.setChecked(bool(s.get("pdf", {}).get("watermark_enabled", True)))
        self.pdf_footer.setChecked(bool(s.get("pdf", {}).get("show_footer", s.get("tier") == "FREE")))
        self.footer_text.setText(s.get("pdf", {}).get("footer_text", "Powered by BU1ST SnapQuote™"))
        self.business_name.setText(s.get("branding", {}).get("business_name", ""))
        self.business_email.setText(s.get("branding", {}).get("email", ""))
        self.business_phone.setText(s.get("branding", {}).get("phone", ""))
        self.logo_path.setText(s.get("branding", {}).get("logo_path", ""))
        self.require_login.setChecked(bool(s.get("security", {}).get("require_login", True)))
        self.auto_lock.setValue(int(s.get("security", {}).get("auto_lock_minutes", 0)))

    def _save(self) -> None:
        self.settings.update(
            {
                "theme": self.theme.currentText(),
                "language": self.language.currentText(),
                "currency": self.currency.currentText(),
                "last_region": self.default_region.text().strip() or "DEFAULT",
                "last_urgency": self.default_urgency.currentText(),
                "tier": self.default_tier.currentText(),
                "pdf": {
                    "watermark_enabled": self.pdf_watermark.isChecked(),
                    "show_footer": self.pdf_footer.isChecked(),
                    "footer_text": self.footer_text.text().strip() or "Powered by BU1ST SnapQuote™",
                },
                "branding": {
                    "business_name": self.business_name.text().strip(),
                    "email": self.business_email.text().strip(),
                    "phone": self.business_phone.text().strip(),
                    "logo_path": self.logo_path.text().strip(),
                },
                "security": {
                    "require_login": self.require_login.isChecked(),
                    "auto_lock_minutes": self.auto_lock.value(),
                },
            }
        )
        save_settings(self.settings)
        self.settings_changed.emit(self.settings)

    def _logout(self) -> None:
        clear_session()
        self.logout_requested.emit()
