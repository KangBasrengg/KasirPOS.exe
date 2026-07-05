"""
Modul untuk komunikasi client ke server lewat HTTP (REST API).
"""
import requests

DEFAULT_TIMEOUT = 8


class ApiClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def test_connection(self):
        r = requests.get(self._url("/"), timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return r.json()

    def login(self, username: str, password: str):
        r = requests.post(self._url("/login"), json={"username": username, "password": password}, timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:
            raise Exception(r.json().get("detail", "Login gagal"))
        return r.json()

    # ---------- Produk ----------
    def list_products(self, search: str = ""):
        r = requests.get(self._url("/products"), params={"search": search}, timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return r.json()

    def get_product_by_barcode(self, barcode: str):
        r = requests.get(self._url(f"/products/barcode/{barcode}"), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:
            return None
        return r.json()

    def create_product(self, data: dict):
        r = requests.post(self._url("/products"), json=data, timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:
            raise Exception(r.json().get("detail", "Gagal menambah produk"))
        return r.json()

    def update_product(self, product_id: int, data: dict):
        r = requests.put(self._url(f"/products/{product_id}"), json=data, timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:
            raise Exception(r.json().get("detail", "Gagal update produk"))
        return r.json()

    def delete_product(self, product_id: int):
        r = requests.delete(self._url(f"/products/{product_id}"), timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:
            raise Exception(r.json().get("detail", "Gagal hapus produk"))
        return r.json()

    def low_stock_products(self):
        r = requests.get(self._url("/products/low-stock/list"), timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return r.json()

    # ---------- Transaksi ----------
    def create_transaction(self, kasir_username: str, items: list, diskon: float, uang_diterima: float):
        payload = {
            "kasir_username": kasir_username,
            "items": items,
            "diskon": diskon,
            "uang_diterima": uang_diterima,
        }
        r = requests.post(self._url("/transactions"), json=payload, timeout=DEFAULT_TIMEOUT)
        if r.status_code != 200:
            raise Exception(r.json().get("detail", "Transaksi gagal"))
        return r.json()

    def list_transactions(self, limit: int = 50):
        r = requests.get(self._url("/transactions"), params={"limit": limit}, timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return r.json()

    # ---------- Laporan ----------
    def sales_today(self):
        r = requests.get(self._url("/reports/sales-today"), timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return r.json()

    def sales_range(self, start_date: str, end_date: str):
        r = requests.get(self._url("/reports/sales-range"), params={"start_date": start_date, "end_date": end_date}, timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return r.json()

    def top_products(self, limit: int = 10):
        r = requests.get(self._url("/reports/top-products"), params={"limit": limit}, timeout=DEFAULT_TIMEOUT)
        r.raise_for_status()
        return r.json()
