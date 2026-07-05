"""
Window utama aplikasi setelah login berhasil. Berisi tab Kasir, Produk, Laporan.
"""
from PyQt5.QtWidgets import (
    QMainWindow, QTabWidget, QWidget, QVBoxLayout, QLabel,
    QHBoxLayout, QPushButton
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from kasir_tab import KasirTab
from produk_tab import ProdukTab
from laporan_tab import LaporanTab
from themes import get_theme


class MainWindow(QMainWindow):
    def __init__(self, client, user_data: dict, on_logout, toggle_theme_callback, current_theme):
        super().__init__()
        self.client = client
        self.user_data = user_data
        self.on_logout = on_logout
        self.toggle_theme = toggle_theme_callback
        self.current_theme = current_theme

        self.setWindowTitle(f"POS Kasir Minimarket - Login sebagai {user_data['username']} ({user_data['role']})")
        self.resize(1100, 700)
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        layout = QVBoxLayout()

        theme = get_theme(self.current_theme)

        # Header bar
        header = QHBoxLayout()
        header.setContentsMargins(8, 4, 8, 4)

        display_name = self.user_data.get('nama_lengkap') or self.user_data['username']
        role_text = self.user_data['role'].upper()
        self.info_label = QLabel(f"{display_name}  |  Role: {role_text}")
        self.info_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
        header.addWidget(self.info_label)
        header.addStretch()

        # Theme toggle
        self.theme_btn = QPushButton("Light Mode" if self.current_theme == "dark" else "Dark Mode")
        self.theme_btn.setFixedHeight(32)
        self.theme_btn.setCursor(Qt.PointingHandCursor)
        self.theme_btn.clicked.connect(self._handle_toggle_theme)
        header.addWidget(self.theme_btn)

        logout_btn = QPushButton("Logout")
        logout_btn.setObjectName("btn_danger")
        logout_btn.setFixedHeight(32)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.clicked.connect(self.handle_logout)
        header.addWidget(logout_btn)

        layout.addLayout(header)

        # Tabs (no emojis)
        self.tabs = QTabWidget()
        self.kasir_tab = KasirTab(self.client, self.user_data)
        self.tabs.addTab(self.kasir_tab, "Kasir")

        if self.user_data["role"] == "admin":
            self.produk_tab = ProdukTab(self.client)
            self.laporan_tab = LaporanTab(self.client)
            self.tabs.addTab(self.produk_tab, "Produk")
            self.tabs.addTab(self.laporan_tab, "Laporan")

        layout.addWidget(self.tabs)
        central.setLayout(layout)
        self.setCentralWidget(central)

    def _handle_toggle_theme(self):
        self.toggle_theme()
        new = "light" if self.current_theme == "dark" else "dark"
        self.current_theme = new
        self.theme_btn.setText("Light Mode" if new == "dark" else "Dark Mode")

    def update_theme(self, theme: dict):
        """Called by AppController after theme toggle to refresh inline styles."""
        self.current_theme = theme["name"]
        self.theme_btn.setText("Light Mode" if theme["name"] == "dark" else "Dark Mode")
        # Refresh inline styles on kasir tab
        if hasattr(self, 'kasir_tab'):
            self.kasir_tab.update_inline_styles(theme)

    def handle_logout(self):
        self.on_logout()
