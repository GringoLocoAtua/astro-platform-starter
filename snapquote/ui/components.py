from __future__ import annotations

from PyQt6.QtCore import QEvent, QPoint, QRect, QSize, Qt, QTimer
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.theme import SPACING, apply_card_shadow


class FlowLayout(QLayout):
    def __init__(self, parent: QWidget | None = None, margin: int = 0, h_spacing: int = 8, v_spacing: int = 8):
        super().__init__(parent)
        self._items = []
        self._h_spacing = h_spacing
        self._v_spacing = v_spacing
        self.setContentsMargins(margin, margin, margin, margin)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(margins.left() + margins.right(), margins.top() + margins.bottom())
        return size

    def _do_layout(self, rect: QRect, test_only: bool):
        x = rect.x()
        y = rect.y()
        line_height = 0
        for item in self._items:
            hint = item.sizeHint()
            next_x = x + hint.width() + self._h_spacing
            if next_x - self._h_spacing > rect.right() and line_height > 0:
                x = rect.x()
                y += line_height + self._v_spacing
                next_x = x + hint.width() + self._h_spacing
                line_height = 0
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), hint))
            x = next_x
            line_height = max(line_height, hint.height())
        return y + line_height - rect.y()


class Card(QFrame):
    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("card")
        apply_card_shadow(self)
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(SPACING["md"], SPACING["md"], SPACING["md"], SPACING["md"])
        self._layout.setSpacing(SPACING["sm"])

    @property
    def content_layout(self) -> QVBoxLayout:
        return self._layout


class SectionHeader(QWidget):
    def __init__(self, title: str, description: str = "", right_widget: QWidget | None = None):
        super().__init__()
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        left = QVBoxLayout()
        left.setContentsMargins(0, 0, 0, 0)
        title_label = QLabel(title)
        title_label.setObjectName("title")
        title_label.setStyleSheet("font-size:16px;")
        left.addWidget(title_label)
        if description:
            subtitle = QLabel(description)
            subtitle.setObjectName("subtitle")
            left.addWidget(subtitle)
        row.addLayout(left, 1)
        if right_widget is not None:
            row.addWidget(right_widget)


class PrimaryButton(QPushButton):
    def __init__(self, text: str):
        super().__init__(text)
        self.setObjectName("primary")


class SecondaryButton(QPushButton):
    def __init__(self, text: str):
        super().__init__(text)
        self.setObjectName("secondary")


class GhostButton(QPushButton):
    def __init__(self, text: str):
        super().__init__(text)
        self.setObjectName("ghost")


class ChipButton(QPushButton):
    def __init__(self, text: str, checked: bool = False):
        super().__init__(text)
        self.setObjectName("chip")
        self.setCheckable(True)
        self.setChecked(checked)


class ToastManager(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self._toast = QLabel(parent)
        self._toast.setVisible(False)
        self._toast.setStyleSheet(
            "background: rgba(22,27,48,0.95); border:1px solid rgba(255,255,255,0.2);"
            "padding:10px 14px; border-radius:10px; color:#eef2ff;"
        )
        self._timer = QTimer(self)
        self._timer.timeout.connect(lambda: self._toast.setVisible(False))

    def show_toast(self, message: str, timeout_ms: int = 2200) -> None:
        self._toast.setText(message)
        self._toast.adjustSize()
        parent_rect = self.parentWidget().rect()
        self._toast.move(parent_rect.right() - self._toast.width() - 24, parent_rect.top() + 20)
        self._toast.setVisible(True)
        self._toast.raise_()
        self._timer.start(timeout_ms)
