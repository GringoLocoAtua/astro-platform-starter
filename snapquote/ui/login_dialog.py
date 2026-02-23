from __future__ import annotations

from PyQt6.QtWidgets import QDialog, QFormLayout, QLineEdit, QMessageBox, QPushButton, QVBoxLayout

from core.auth import create_user, has_users, save_session, verify_user
from ui.i18n import tr


class LoginDialog(QDialog):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(tr("btn.login"))
        self.username = QLineEdit()
        self.password = QLineEdit(); self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()
        form.addRow("Username", self.username)
        form.addRow("Password", self.password)
        layout.addLayout(form)

        self.submit = QPushButton(tr("btn.login"))
        self.submit.clicked.connect(self._submit)
        layout.addWidget(self.submit)

        if not has_users():
            self.setWindowTitle("Create Admin")
            self.submit.setText("Create Admin")

    def _submit(self) -> None:
        user = self.username.text().strip()
        pwd = self.password.text().strip()
        if not user or not pwd:
            QMessageBox.warning(self, "Error", "Username and password required")
            return
        if not has_users():
            create_user(user, pwd, is_admin=True)
            save_session(user)
            self.accept()
            return
        if verify_user(user, pwd):
            save_session(user)
            self.accept()
            return
        QMessageBox.warning(self, "Error", "Invalid credentials")
