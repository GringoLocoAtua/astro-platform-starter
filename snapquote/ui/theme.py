from __future__ import annotations

from PyQt6.QtGui import QColor, QFont
from PyQt6.QtWidgets import QApplication, QGraphicsDropShadowEffect, QWidget

FONT_FAMILY = '"Segoe UI Variable", "Segoe UI", "Inter", "Arial"'

SPACING = {
    "xs": 8,
    "sm": 12,
    "md": 16,
    "lg": 24,
}

RADII = {
    "sm": 10,
    "md": 14,
    "lg": 16,
}

COLORS = {
    "bg": "#0b1020",
    "panel": "rgba(255, 255, 255, 0.06)",
    "panel_soft": "rgba(255, 255, 255, 0.04)",
    "border": "rgba(255, 255, 255, 0.12)",
    "text": "#eef2ff",
    "muted": "#b8c1e0",
    "primary": "#5b8cff",
    "primary_hover": "#6f9aff",
    "secondary": "rgba(255,255,255,0.08)",
}


def build_stylesheet() -> str:
    return f"""
    * {{
        font-family: {FONT_FAMILY};
        color: {COLORS['text']};
    }}
    QMainWindow, QWidget#rootWindow {{
        background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #0b1020, stop:1 #151d36);
    }}
    QFrame#card {{
        background: {COLORS['panel']};
        border: 1px solid {COLORS['border']};
        border-radius: {RADII['md']}px;
    }}
    QLabel#title {{
        font-size: 22px;
        font-weight: 700;
    }}
    QLabel#subtitle {{
        color: {COLORS['muted']};
        font-size: 12px;
    }}
    QLabel#totalValue {{
        font-size: 44px;
        font-weight: 700;
    }}
    QLabel#badge {{
        background: rgba(91,140,255,0.2);
        border: 1px solid rgba(91,140,255,0.45);
        border-radius: 10px;
        padding: 2px 8px;
        font-size: 11px;
        color: #dfe8ff;
    }}
    QLineEdit, QTextEdit, QSpinBox, QComboBox, QListWidget, QTreeWidget, QToolButton {{
        background: {COLORS['panel_soft']};
        border: 1px solid {COLORS['border']};
        border-radius: {RADII['sm']}px;
        padding: 6px;
    }}
    QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QComboBox:focus {{
        border: 1px solid {COLORS['primary']};
    }}
    QPushButton {{
        border-radius: {RADII['sm']}px;
        padding: 8px 14px;
        border: 1px solid transparent;
    }}
    QPushButton#primary {{
        background: {COLORS['primary']};
        color: white;
        font-weight: 600;
    }}
    QPushButton#primary:hover {{
        background: {COLORS['primary_hover']};
    }}
    QPushButton#secondary {{
        background: {COLORS['secondary']};
        border: 1px solid {COLORS['border']};
    }}
    QPushButton#ghost {{
        background: transparent;
        border: 1px solid {COLORS['border']};
        color: {COLORS['muted']};
    }}
    QPushButton#chip {{
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 14px;
        padding: 4px 10px;
    }}
    QPushButton#chip:checked {{
        background: rgba(91,140,255,0.28);
        border: 1px solid rgba(111,154,255,0.8);
    }}
    QSplitter::handle {{
        background: rgba(255,255,255,0.09);
        width: 1px;
    }}
    """


def make_shadow(radius: int = 28, alpha: int = 90) -> QGraphicsDropShadowEffect:
    shadow = QGraphicsDropShadowEffect()
    shadow.setBlurRadius(radius)
    shadow.setOffset(0, 10)
    shadow.setColor(QColor(0, 0, 0, alpha))
    return shadow


def apply_card_shadow(widget: QWidget) -> None:
    widget.setGraphicsEffect(make_shadow())


def apply_theme(app: QApplication) -> None:
    app.setStyleSheet(build_stylesheet())
    font = QFont("Segoe UI")
    font.setPointSize(10)
    app.setFont(font)
