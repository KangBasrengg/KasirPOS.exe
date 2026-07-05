"""
POS Kasir - Aplikasi Client (Desktop)
======================================
Entry point aplikasi. Jalankan dengan: python main.py
Untuk build .exe, lihat README.md di folder utama proyek.
"""
import sys
from PyQt5.QtWidgets import QApplication

from login_window import LoginWindow
from main_window import MainWindow
from config import load_config, save_config
from themes import get_theme, build_stylesheet


class AppController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setStyle("Fusion")
        self.config = load_config()
        self.main_window = None
        self.login_window = None
        self._apply_theme(self.config.get("theme", "dark"))
        self.show_login()

    def _apply_theme(self, theme_name: str):
        """Apply theme globally to the entire application."""
        self.current_theme_name = theme_name
        theme = get_theme(theme_name)
        stylesheet = build_stylesheet(theme)
        self.app.setStyleSheet(stylesheet)

    def toggle_theme(self):
        """Switch between light and dark theme."""
        new_name = "light" if self.current_theme_name == "dark" else "dark"
        self._apply_theme(new_name)
        self.config["theme"] = new_name
        save_config(self.config)
        # Re-apply any inline styles that depend on theme
        if self.main_window:
            self.main_window.update_theme(get_theme(new_name))

    def show_login(self):
        self.login_window = LoginWindow(self.handle_login_success, self.toggle_theme, self.current_theme_name)
        self.login_window.show()

    def handle_login_success(self, client, user_data):
        self.login_window.close()
        self.main_window = MainWindow(
            client, user_data, self.handle_logout, self.toggle_theme, self.current_theme_name
        )
        self.main_window.show()

    def handle_logout(self):
        self.main_window.close()
        self.show_login()

    def run(self):
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    controller = AppController()
    controller.run()
