from __future__ import annotations

from pathlib import Path

from PyQt6.QtWidgets import QFileDialog, QHBoxLayout, QMessageBox, QPushButton, QVBoxLayout, QWidget, QMainWindow

from core.industry_registry import IndustryRegistry
from core.quote_builder import build_quote
from export.pdf_generator import generate_quote_pdf
from ui.quote_form import QuoteForm
from ui.results_panel import ResultsPanel


DARK_THEME = """
QWidget { background-color: #151820; color: #E6EAF2; font-size: 13px; }
QPushButton { background: #334155; border: 1px solid #475569; padding: 6px 10px; border-radius: 6px; }
QLineEdit, QTextEdit, QComboBox, QListWidget, QSpinBox { background: #0f172a; border: 1px solid #334155; border-radius: 6px; }
QGroupBox { border: 1px solid #334155; margin-top: 8px; }
"""


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.registry = IndustryRegistry()
        self.current_quote: dict | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        self.setWindowTitle("SnapQuote v2")
        self.resize(1200, 700)
        self.setStyleSheet(DARK_THEME)

        central = QWidget()
        root = QVBoxLayout(central)
        split = QHBoxLayout()

        self.form = QuoteForm(self.registry.list_industries())
        self.results = ResultsPanel()
        split.addWidget(self.form, 1)
        split.addWidget(self.results, 1)

        self.generate_btn = QPushButton("Generate Quote")
        self.export_btn = QPushButton("Export PDF")
        self.clear_btn = QPushButton("Clear")

        self.generate_btn.clicked.connect(self._generate)
        self.export_btn.clicked.connect(self._export_pdf)
        self.clear_btn.clicked.connect(self._clear)
        self.form.industry.currentIndexChanged.connect(self._industry_changed)

        btns = QHBoxLayout()
        btns.addWidget(self.generate_btn)
        btns.addWidget(self.export_btn)
        btns.addWidget(self.clear_btn)

        root.addLayout(split)
        root.addLayout(btns)
        self.setCentralWidget(central)

        self._industry_changed(0)

    def _industry_changed(self, _: int) -> None:
        industry_id = self.form.industry.currentData()
        industry = self.registry.get_industry(industry_id)
        self.form.set_addons(sorted(industry.get("addons", {}).keys()))

    def _generate(self) -> None:
        self.current_quote = build_quote(self.form.values())
        self.results.show_quote(self.current_quote)

    def _export_pdf(self) -> None:
        if not self.current_quote or "error" in self.current_quote:
            QMessageBox.warning(self, "No Quote", "Generate a quote first.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", str(Path.home() / "quote.pdf"), "PDF files (*.pdf)")
        if not path:
            return
        industry_name = self.form.industry.currentText()
        output = generate_quote_pdf(
            quote=self.current_quote,
            output_path=path,
            industry_name=industry_name,
            scope_text=self.form.scope.toPlainText(),
            tier=self.form.tier.currentText(),
            show_footer=False,
        )
        QMessageBox.information(self, "Exported", f"Saved PDF to {output}")

    def _clear(self) -> None:
        self.form.clear_form()
        self.results.show_quote({"currency": "AUD", "total": 0, "breakdown": [], "applied_modifiers": {}, "assumptions": []})
