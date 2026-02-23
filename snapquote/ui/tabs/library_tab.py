from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QVBoxLayout, QWidget

from core.constants import DATA_DIR
from core.quote_store import delete_quote, list_quotes, load_quote, save_quote
from export.pdf_generator import generate_quote_pdf
from ui.components import Card, GhostButton, PrimaryButton, SecondaryButton


class LibraryTab(QWidget):
    def __init__(self) -> None:
        super().__init__()
        root = QVBoxLayout(self)
        card = Card()
        card.content_layout.addWidget(QLabel("Quote Library"))
        self.list_widget = QListWidget()

        actions = QHBoxLayout()
        self.export_btn = SecondaryButton("Export PDF Again")
        self.delete_btn = GhostButton("Delete")
        self.duplicate_btn = SecondaryButton("Duplicate")
        self.open_folder_btn = PrimaryButton("Open Folder")
        actions.addWidget(self.export_btn)
        actions.addWidget(self.delete_btn)
        actions.addWidget(self.duplicate_btn)
        actions.addWidget(self.open_folder_btn)

        self.details = QLabel("Select a quote")
        self.details.setWordWrap(True)

        card.content_layout.addWidget(self.list_widget)
        card.content_layout.addLayout(actions)
        card.content_layout.addWidget(self.details)
        root.addWidget(card)

        self.list_widget.currentItemChanged.connect(self._show_details)
        self.open_folder_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl.fromLocalFile(str(DATA_DIR))))
        self.delete_btn.clicked.connect(self._delete_selected)
        self.duplicate_btn.clicked.connect(self._duplicate_selected)
        self.export_btn.clicked.connect(self._export_selected)

        self.refresh()

    def refresh(self) -> None:
        self.list_widget.clear()
        for item in list_quotes():
            label = f"{item.get('timestamp','')} | {item.get('industry_name','')} | {item.get('currency','AUD')} {item.get('total',0)} | {item.get('client_name','')}"
            widget_item = QListWidgetItem(label)
            widget_item.setData(Qt.ItemDataRole.UserRole, item.get("id"))
            self.list_widget.addItem(widget_item)

    def _current_quote(self) -> dict | None:
        item = self.list_widget.currentItem()
        if not item:
            return None
        quote_id = item.data(Qt.ItemDataRole.UserRole)
        return load_quote(quote_id)

    def _show_details(self) -> None:
        quote = self._current_quote()
        if not quote:
            self.details.setText("Select a quote")
            return
        self.details.setText(
            f"Industry: {quote.get('industry_name')}\nClient: {quote.get('client_name')}\nTotal: {quote.get('currency')} {quote.get('total')}\nScope: {quote.get('scope_text','')}"
        )

    def _delete_selected(self) -> None:
        quote = self._current_quote()
        if not quote:
            return
        delete_quote(quote.get("id"))
        self.refresh()

    def _duplicate_selected(self) -> None:
        quote = self._current_quote()
        if not quote:
            return
        payload = dict(quote)
        payload.pop("id", None)
        save_quote(payload)
        self.refresh()

    def _export_selected(self) -> None:
        quote = self._current_quote()
        if not quote:
            return
        out = DATA_DIR / f"quote-{quote.get('id','copy')}.pdf"
        generate_quote_pdf(
            quote=quote.get("quote", quote),
            output_path=str(out),
            industry_name=quote.get("industry_name", "Industry"),
            scope_text=quote.get("scope_text", ""),
            tier=quote.get("quote", {}).get("tier", "FREE"),
            settings={},
        )
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(out)))
