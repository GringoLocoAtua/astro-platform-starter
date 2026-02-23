from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFormLayout, QLabel, QLineEdit, QMessageBox, QPushButton, QVBoxLayout, QWidget

from core.auth import has_users, save_session, verify_user, create_user


class ProfileTab(QWidget):
    logged_in = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self.username = QLineEdit()
        self.pin = QLineEdit(); self.pin.setEchoMode(QLineEdit.EchoMode.Password)
        self.status = QLabel("Not logged in")
        self.login_btn = QPushButton("Login")
        form.addRow("Username", self.username)
        form.addRow("PIN", self.pin)
        layout.addLayout(form)
        layout.addWidget(self.login_btn)
        layout.addWidget(self.status)
        layout.addStretch(1)

        self.login_btn.clicked.connect(self._login)

    def _login(self) -> None:
        user = self.username.text().strip()
        pin = self.pin.text().strip()
        if not user or not pin:
            QMessageBox.warning(self, "Profile", "Username and PIN required")
            return
        if not has_users():
            create_user(user, pin, is_admin=True)
            save_session(user)
            self.status.setText(f"Logged in: {user}")
            self.logged_in.emit(user)
            return
        if verify_user(user, pin):
            save_session(user)
            self.status.setText(f"Logged in: {user}")
            self.logged_in.emit(user)
        else:
            QMessageBox.warning(self, "Profile", "Invalid credentials")
