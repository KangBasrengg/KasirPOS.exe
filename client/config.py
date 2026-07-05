"""
Menyimpan konfigurasi client (alamat IP server, tema) ke file config.json
supaya tidak perlu input ulang tiap buka aplikasi.
"""
import json
import os

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "server_url": "http://127.0.0.1:8000",
    "theme": "dark",
}


def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                # Ensure new keys exist
                for key, val in DEFAULT_CONFIG.items():
                    if key not in config:
                        config[key] = val
                return config
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
