from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ui.components import Card, ChipButton, FlowLayout, SectionHeader


class PhotoPanel(QWidget):
    images_changed = pyqtSignal(list)
    tags_changed = pyqtSignal(list)
    refresh_tags_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self._image_paths: list[str] = []
        self._manual_tags: set[str] = set()
        self._tag_chips: dict[str, ChipButton] = {}
        self._setup_ui()

    def _setup_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)

        card = Card()
        card.content_layout.addWidget(SectionHeader("Media & Tags", "Confirm photo-derived tags"))

        controls = QHBoxLayout()
        self.add_images_btn = QPushButton("Add Images")
        self.remove_image_btn = QPushButton("Remove")
        self.refresh_tags_btn = QPushButton("Refresh Tags")
        self.refresh_tags_btn.setObjectName("secondary")
        controls.addWidget(self.add_images_btn)
        controls.addWidget(self.remove_image_btn)
        controls.addWidget(self.refresh_tags_btn)

        self.thumb_list = QListWidget()
        self.thumb_list.setViewMode(QListWidget.ViewMode.IconMode)
        self.thumb_list.setResizeMode(QListWidget.ResizeMode.Adjust)
        self.thumb_list.setGridSize(QSize(100, 100))
        self.thumb_list.setIconSize(QSize(74, 74))
        self.thumb_list.setSpacing(8)

        tags_holder = QWidget()
        self.tags_flow = FlowLayout(tags_holder, h_spacing=8, v_spacing=8)

        manual = QHBoxLayout()
        self.manual_tag_input = QLineEdit()
        self.manual_tag_input.setPlaceholderText("Add manual tag")
        self.add_manual_btn = QPushButton("Add Tag")
        self.add_manual_btn.setObjectName("secondary")
        manual.addWidget(self.manual_tag_input)
        manual.addWidget(self.add_manual_btn)

        self.applied_list = QListWidget()
        self.applied_list.setMaximumHeight(120)

        card.content_layout.addLayout(controls)
        card.content_layout.addWidget(self.thumb_list)
        card.content_layout.addWidget(tags_holder)
        card.content_layout.addLayout(manual)
        card.content_layout.addWidget(self.applied_list)
        root.addWidget(card)

        self.add_images_btn.clicked.connect(self._add_images)
        self.remove_image_btn.clicked.connect(self._remove_selected)
        self.refresh_tags_btn.clicked.connect(self.refresh_tags_requested.emit)
        self.add_manual_btn.clicked.connect(self._add_manual_tag)

    def _add_images(self) -> None:
        from PyQt6.QtWidgets import QFileDialog

        files, _ = QFileDialog.getOpenFileNames(self, "Choose images")
        if files:
            merged = list(dict.fromkeys(self._image_paths + files))
            self.set_images(merged)

    def _remove_selected(self) -> None:
        selected = {item.data(256) for item in self.thumb_list.selectedItems()}
        self.set_images([path for path in self._image_paths if path not in selected])

    def _add_manual_tag(self) -> None:
        tag = self.manual_tag_input.text().strip().lower()
        self.manual_tag_input.clear()
        if not tag:
            return
        self._manual_tags.add(tag)
        if tag not in self._tag_chips:
            chip = ChipButton(tag, checked=True)
            chip.toggled.connect(self._emit_tags)
            self._tag_chips[tag] = chip
            self.tags_flow.addWidget(chip)
        self._emit_tags()

    def set_images(self, paths: list[str]) -> None:
        self._image_paths = list(paths)
        self.thumb_list.clear()
        for path in self._image_paths:
            item = QListWidgetItem(Path(path).name)
            item.setData(256, path)
            if Path(path).exists():
                pix = QPixmap(path)
                if not pix.isNull():
                    item.setIcon(QIcon(pix.scaled(74, 74)))
            self.thumb_list.addItem(item)
        self.images_changed.emit(list(self._image_paths))

    def set_detected_tags(self, tags: list[str]) -> None:
        for chip in self._tag_chips.values():
            chip.deleteLater()
        self._tag_chips = {}
        for tag in sorted(set(tags) | self._manual_tags):
            chip = ChipButton(tag, checked=True)
            chip.toggled.connect(self._emit_tags)
            self._tag_chips[tag] = chip
            self.tags_flow.addWidget(chip)
        self._emit_tags()

    def set_applied_from_photos(self, applied_lines: list[str]) -> None:
        self.applied_list.clear()
        if not applied_lines:
            self.applied_list.addItem("Applied From Photos: none")
            return
        for line in applied_lines:
            self.applied_list.addItem(line)

    def get_confirmed_tags(self) -> list[str]:
        tags = [tag for tag, chip in self._tag_chips.items() if chip.isChecked()]
        return sorted(set(tags))

    def _emit_tags(self) -> None:
        self.tags_changed.emit(self.get_confirmed_tags())

    def clear_panel(self) -> None:
        self._manual_tags.clear()
        self.set_images([])
        self.set_detected_tags([])
        self.applied_list.clear()
