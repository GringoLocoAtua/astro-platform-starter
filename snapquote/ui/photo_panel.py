from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class PhotoPanel(QWidget):
    images_changed = pyqtSignal(list)
    tags_changed = pyqtSignal(list)
    refresh_tags_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self._image_paths: list[str] = []
        self._manual_tags: set[str] = set()
        self._tag_checks: dict[str, QCheckBox] = {}
        self._setup_ui()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.addWidget(QLabel("Photos & Tags"))

        img_box = QGroupBox("Selected Photos")
        img_layout = QVBoxLayout(img_box)
        btn_layout = QHBoxLayout()
        self.add_images_btn = QPushButton("Add Images")
        self.remove_image_btn = QPushButton("Remove Selected")
        self.refresh_tags_btn = QPushButton("Refresh Tags")
        btn_layout.addWidget(self.add_images_btn)
        btn_layout.addWidget(self.remove_image_btn)
        btn_layout.addWidget(self.refresh_tags_btn)
        img_layout.addLayout(btn_layout)

        self.thumb_list = QListWidget()
        self.thumb_list.setIconSize(QSize(72, 72))
        img_layout.addWidget(self.thumb_list)

        tags_box = QGroupBox("Confirmed Tags")
        tags_layout = QVBoxLayout(tags_box)
        self.detected_tags_wrap = QVBoxLayout()
        tags_layout.addLayout(self.detected_tags_wrap)

        manual = QHBoxLayout()
        self.manual_tag_input = QLineEdit()
        self.manual_tag_input.setPlaceholderText("manual_tag")
        self.add_manual_btn = QPushButton("Add Tag")
        manual.addWidget(self.manual_tag_input)
        manual.addWidget(self.add_manual_btn)
        tags_layout.addLayout(manual)

        root.addWidget(img_box)
        root.addWidget(tags_box)

        self.add_images_btn.clicked.connect(self._add_images)
        self.remove_image_btn.clicked.connect(self._remove_selected)
        self.refresh_tags_btn.clicked.connect(self.refresh_tags_requested.emit)
        self.add_manual_btn.clicked.connect(self._add_manual_tag)

    def _add_images(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(self, "Choose images")
        if not files:
            return
        merged = list(dict.fromkeys(self._image_paths + files))
        self.set_images(merged)

    def _remove_selected(self) -> None:
        remove_rows = {item.text() for item in self.thumb_list.selectedItems()}
        if not remove_rows:
            return
        self.set_images([p for p in self._image_paths if p not in remove_rows])

    def _add_manual_tag(self) -> None:
        tag = self.manual_tag_input.text().strip().lower()
        self.manual_tag_input.clear()
        if not tag:
            return
        self._manual_tags.add(tag)
        self._emit_tags()

    def set_images(self, paths: list[str]) -> None:
        self._image_paths = list(paths)
        self.thumb_list.clear()
        for path in self._image_paths:
            item = QListWidgetItem(path)
            if Path(path).exists():
                pix = QPixmap(path)
                if not pix.isNull():
                    item.setIcon(QIcon(pix.scaled(72, 72)))
            self.thumb_list.addItem(item)
        self.images_changed.emit(list(self._image_paths))

    def set_detected_tags(self, tags: list[str]) -> None:
        while self.detected_tags_wrap.count():
            child = self.detected_tags_wrap.takeAt(0)
            widget = child.widget()
            if widget is not None:
                widget.deleteLater()
        self._tag_checks.clear()
        for tag in sorted(set(tags)):
            check = QCheckBox(tag)
            check.setChecked(True)
            check.toggled.connect(self._emit_tags)
            self.detected_tags_wrap.addWidget(check)
            self._tag_checks[tag] = check
        self._emit_tags()

    def get_confirmed_tags(self) -> list[str]:
        active = [tag for tag, check in self._tag_checks.items() if check.isChecked()]
        active.extend(sorted(self._manual_tags))
        return sorted(set(active))

    def _emit_tags(self) -> None:
        self.tags_changed.emit(self.get_confirmed_tags())

    def clear_panel(self) -> None:
        self._manual_tags.clear()
        self.set_images([])
        self.set_detected_tags([])
