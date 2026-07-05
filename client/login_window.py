"""
Window login. Juga tempat mengatur alamat IP server (untuk koneksi multi-komputer).
"""
from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QMessageBox, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon

from api_client import ApiClient
from config import load_config, save_config
from themes import get_theme


class LoginWindow(QWidget):
    def __init__(self, on_login_success, toggle_theme_callback, current_theme):
        super().__init__()
        self.on_login_success = on_login_success
        self.toggle_theme = toggle_theme_callback
        self.current_theme = current_theme
        self.config = load_config()
        self.setWindowTitle("Login - POS Kasir Minimarket")
        self.setFixedSize(440, 480)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 24, 40, 30)
        layout.setSpacing(12)

        # Top right: theme toggle
        top_bar = QHBoxLayout()
        top_bar.addStretch()
        self.theme_btn = QPushButton("Light Mode" if self.current_theme == "dark" else "Dark Mode")
        self.theme_btn.setFixedHeight(32)
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(self._handle_toggle_theme)
        top_bar.addWidget(self.theme_btn)
        layout.addLayout(top_bar)

        # Title
        title = QLabel("POS KASIR")
        title.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        subtitle = QLabel("Sistem Manajemen Kasir Minimarket")
        subtitle.setAlignment(Qt.AlignCenter)
        theme = get_theme(self.current_theme)
        subtitle.setStyleSheet(f"color: {theme['text_muted']};")

        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(8)

        # Alamat server
        server_label = QLabel("Alamat Server:")
        server_label.setFont(QFont("Segoe UI", 11))
        self.server_input = QLineEdit(self.config.get("server_url", "http://127.0.0.1:8000"))
        self.server_input.setPlaceholderText("http://192.168.1.10:8000")
        self.server_input.setMinimumHeight(36)
        layout.addWidget(server_label)
        layout.addWidget(self.server_input)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        layout.addWidget(line)

        # Username / password
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setMinimumHeight(36)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setMinimumHeight(36)
        self.password_input.returnPressed.connect(self.handle_login)

        usr_label = QLabel("Username:")
        usr_label.setFont(QFont("Segoe UI", 11))
        pwd_label = QLabel("Password:")
        pwd_label.setFont(QFont("Segoe UI", 11))

        layout.addWidget(usr_label)
        layout.addWidget(self.username_input)
        layout.addWidget(pwd_label)
        layout.addWidget(self.password_input)
        layout.addSpacing(4)

        btn_layout = QHBoxLayout()
        self.test_btn = QPushButton("Tes Koneksi")
        self.test_btn.setMinimumHeight(38)
        self.test_btn.setCursor(Qt.PointingHandCursor)
        self.test_btn.clicked.connect(self.handle_test_connection)

        self.login_btn = QPushButton("Masuk")
        self.login_btn.setObjectName("btn_primary")
        self.login_btn.setDefault(True)
        self.login_btn.setMinimumHeight(38)
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.clicked.connect(self.handle_login)

        btn_layout.addWidget(self.test_btn)
        btn_layout.addWidget(self.login_btn)
        layout.addLayout(btn_layout)

        hint = QLabel("Default: admin/admin123 (admin) atau kasir1/kasir123 (kasir)")
        hint.setStyleSheet(f"color: {theme['text_muted']}; font-size: 11px;")
        hint.setAlignment(Qt.AlignCenter)
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.setLayout(layout)

    def _handle_toggle_theme(self):
        self.toggle_theme()
        new = "light" if self.current_theme == "dark" else "dark"
        self.current_theme = new
        self.theme_btn.setText("Light Mode" if new == "dark" else "Dark Mode")

    def handle_test_connection(self):
        url = self.server_input.text().strip()
        try:
            client = ApiClient(url)
            client.test_connection()
            QMessageBox.information(self, "Sukses", "Berhasil terhubung ke server!")
        except Exception as e:
            QMessageBox.critical(self, "Gagal", f"Tidak bisa terhubung ke server:\n{e}")

    def handle_login(self):
        url = self.server_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not url or not username or not password:
            QMessageBox.warning(self, "Peringatan", "Alamat server, username, dan password harus diisi.")
            return

        self.config["server_url"] = url
        save_config(self.config)

        try:
            client = ApiClient(url)
            user_data = client.login(username, password)
        except Exception as e:
            QMessageBox.critical(self, "Login Gagal", str(e))
            return

        self.on_login_success(client, user_data)
