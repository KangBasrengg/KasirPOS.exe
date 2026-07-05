"""
Tab Kasir: layar transaksi penjualan (POS).
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QDoubleSpinBox, QHeaderView,
    QTextEdit, QDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

from themes import get_theme
from config import load_config


def format_rupiah(value):
    return f"Rp {value:,.0f}".replace(",", ".")


class ReceiptDialog(QDialog):
    """Menampilkan struk setelah transaksi berhasil, dengan opsi cetak."""
    def __init__(self, parent, receipt_text: str):
        super().__init__(parent)
        self.setWindowTitle("Struk Transaksi")
        self.setMinimumSize(400, 520)
        self.receipt_text = receipt_text

        layout = QVBoxLayout()
        self.text_area = QTextEdit()
        self.text_area.setPlainText(receipt_text)
        self.text_area.setFont(QFont("Courier New", 10))
        self.text_area.setReadOnly(True)
        layout.addWidget(self.text_area)

        btn_layout = QHBoxLayout()
        print_btn = QPushButton("Cetak Struk")
        print_btn.setObjectName("btn_primary")
        print_btn.setMinimumHeight(36)
        print_btn.setCursor(Qt.PointingHandCursor)
        print_btn.clicked.connect(self.handle_print)

        close_btn = QPushButton("Tutup")
        close_btn.setMinimumHeight(36)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.clicked.connect(self.accept)

        btn_layout.addWidget(print_btn)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def handle_print(self):
        printer = QPrinter()
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QDialog.Accepted:
            self.text_area.print_(printer)


class KasirTab(QWidget):
    def __init__(self, client, user_data: dict):
        super().__init__()
        self.client = client
        self.user_data = user_data
        self.cart = []  # list of dict: product_id, nama, harga, jumlah
        config = load_config()
        self._theme = get_theme(config.get("theme", "dark"))
        self._build_ui()

    def _build_ui(self):
        main_layout = QHBoxLayout()

        # ---------- Kiri: cari & pilih produk ----------
        left_layout = QVBoxLayout()

        search_header = QLabel("Cari / Scan Barcode Produk")
        search_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        left_layout.addWidget(search_header)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Scan barcode lalu Enter, atau ketik nama produk...")
        self.search_input.setMinimumHeight(38)
        self.search_input.returnPressed.connect(self.handle_search_enter)
        left_layout.addWidget(self.search_input)

        self.result_table = QTableWidget(0, 4)
        self.result_table.setHorizontalHeaderLabels(["Nama", "Harga", "Stok", "Barcode"])
        self.result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.result_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.doubleClicked.connect(self.handle_add_selected_to_cart)
        left_layout.addWidget(self.result_table)

        add_btn = QPushButton("Tambah ke Keranjang (double-click juga bisa)")
        add_btn.setObjectName("btn_primary")
        add_btn.setMinimumHeight(36)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.handle_add_selected_to_cart)
        left_layout.addWidget(add_btn)

        main_layout.addLayout(left_layout, 55)

        # ---------- Kanan: keranjang & pembayaran ----------
        right_layout = QVBoxLayout()

        cart_header = QLabel("Keranjang Belanja")
        cart_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
        right_layout.addWidget(cart_header)

        self.cart_table = QTableWidget(0, 5)
        self.cart_table.setHorizontalHeaderLabels(["Nama", "Harga", "Qty", "Subtotal", "Hapus"])
        self.cart_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.cart_table.setAlternatingRowColors(True)
        right_layout.addWidget(self.cart_table)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(8)

        total_row = QHBoxLayout()
        total_row.addWidget(QLabel("Total Belanja:"))
        self.total_label = QLabel(format_rupiah(0))
        self.total_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        total_row.addWidget(self.total_label)
        form_layout.addLayout(total_row)

        diskon_row = QHBoxLayout()
        diskon_row.addWidget(QLabel("Diskon (Rp):"))
        self.diskon_input = QDoubleSpinBox()
        self.diskon_input.setMaximum(999999999)
        self.diskon_input.setDecimals(0)
        self.diskon_input.setMinimumHeight(34)
        self.diskon_input.valueChanged.connect(self.update_totals)
        diskon_row.addWidget(self.diskon_input)
        form_layout.addLayout(diskon_row)

        bayar_row = QHBoxLayout()
        bayar_row.addWidget(QLabel("Total Bayar:"))
        self.total_bayar_label = QLabel(format_rupiah(0))
        self.total_bayar_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.total_bayar_label.setStyleSheet(f"color:{self._theme['accent_blue']};")
        bayar_row.addWidget(self.total_bayar_label)
        form_layout.addLayout(bayar_row)

        uang_row = QHBoxLayout()
        uang_row.addWidget(QLabel("Uang Diterima:"))
        self.uang_input = QDoubleSpinBox()
        self.uang_input.setMaximum(999999999)
        self.uang_input.setDecimals(0)
        self.uang_input.setMinimumHeight(34)
        self.uang_input.valueChanged.connect(self.update_totals)
        uang_row.addWidget(self.uang_input)
        form_layout.addLayout(uang_row)

        kembali_row = QHBoxLayout()
        kembali_row.addWidget(QLabel("Kembalian:"))
        self.kembalian_label = QLabel(format_rupiah(0))
        self.kembalian_label.setFont(QFont("Segoe UI", 13, QFont.Bold))
        self.kembalian_label.setStyleSheet(f"color:{self._theme['accent_green']};")
        kembali_row.addWidget(self.kembalian_label)
        form_layout.addLayout(kembali_row)

        right_layout.addLayout(form_layout)

        action_row = QHBoxLayout()
        clear_btn = QPushButton("Kosongkan Keranjang")
        clear_btn.setMinimumHeight(40)
        clear_btn.setCursor(Qt.PointingHandCursor)
        clear_btn.clicked.connect(self.handle_clear_cart)

        pay_btn = QPushButton("BAYAR (F2)")
        pay_btn.setShortcut("F2")
        pay_btn.setObjectName("btn_success")
        pay_btn.setMinimumHeight(44)
        pay_btn.setFont(QFont("Segoe UI", 13, QFont.Bold))
        pay_btn.setCursor(Qt.PointingHandCursor)
        pay_btn.clicked.connect(self.handle_pay)

        action_row.addWidget(clear_btn)
        action_row.addWidget(pay_btn)
        right_layout.addLayout(action_row)

        main_layout.addLayout(right_layout, 45)
        self.setLayout(main_layout)

        self.handle_search("")  # tampilkan semua produk di awal

    def update_inline_styles(self, theme):
        """Re-apply theme-dependent inline styles."""
        self._theme = theme
        self.total_bayar_label.setStyleSheet(f"color:{theme['accent_blue']};")
        self.kembalian_label.setStyleSheet(f"color:{theme['accent_green']};")

    # ---------- Pencarian produk ----------
    def handle_search_enter(self):
        keyword = self.search_input.text().strip()
        if not keyword:
            return
        # Coba cari sebagai barcode persis dulu (untuk scanner)
        product = self.client.get_product_by_barcode(keyword)
        if product:
            self.add_to_cart(product)
            self.search_input.clear()
            self.handle_search("")
            return
        self.handle_search(keyword)

    def handle_search(self, keyword: str):
        try:
            products = self.client.list_products(search=keyword)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengambil data produk:\n{e}")
            return
        self.result_table.setRowCount(0)
        self._current_results = products
        for row, p in enumerate(products):
            self.result_table.insertRow(row)
            self.result_table.setItem(row, 0, QTableWidgetItem(p["nama"]))
            self.result_table.setItem(row, 1, QTableWidgetItem(format_rupiah(p["harga_jual"])))
            self.result_table.setItem(row, 2, QTableWidgetItem(str(p["stok"])))
            self.result_table.setItem(row, 3, QTableWidgetItem(p.get("barcode") or "-"))

    def handle_add_selected_to_cart(self):
        row = self.result_table.currentRow()
        if row < 0 or row >= len(self._current_results):
            return
        product = self._current_results[row]
        self.add_to_cart(product)

    # ---------- Keranjang ----------
    def add_to_cart(self, product: dict):
        if product["stok"] <= 0:
            QMessageBox.warning(self, "Stok Habis", f"Stok '{product['nama']}' habis.")
            return

        for item in self.cart:
            if item["product_id"] == product["id"]:
                if item["jumlah"] + 1 > product["stok"]:
                    QMessageBox.warning(self, "Stok Tidak Cukup", f"Stok '{product['nama']}' hanya {product['stok']}.")
                    return
                item["jumlah"] += 1
                self._refresh_cart_table()
                return

        self.cart.append({
            "product_id": product["id"],
            "nama": product["nama"],
            "harga": product["harga_jual"],
            "jumlah": 1,
        })
        self._refresh_cart_table()

    def _refresh_cart_table(self):
        self.cart_table.setRowCount(0)
        for row, item in enumerate(self.cart):
            self.cart_table.insertRow(row)
            self.cart_table.setItem(row, 0, QTableWidgetItem(item["nama"]))
            self.cart_table.setItem(row, 1, QTableWidgetItem(format_rupiah(item["harga"])))

            qty_item = QTableWidgetItem(str(item["jumlah"]))
            self.cart_table.setItem(row, 2, qty_item)

            subtotal = item["harga"] * item["jumlah"]
            self.cart_table.setItem(row, 3, QTableWidgetItem(format_rupiah(subtotal)))

            hapus_btn = QPushButton("Hapus")
            hapus_btn.setObjectName("btn_danger")
            hapus_btn.setCursor(Qt.PointingHandCursor)
            hapus_btn.clicked.connect(lambda checked, r=row: self.handle_remove_item(r))
            self.cart_table.setCellWidget(row, 4, hapus_btn)

        self.cart_table.cellChanged.connect(self.handle_qty_edited)
        self.update_totals()

    def handle_qty_edited(self, row, column):
        if column != 2 or row >= len(self.cart):
            return
        try:
            new_qty = int(self.cart_table.item(row, column).text())
            if new_qty <= 0:
                raise ValueError
            self.cart[row]["jumlah"] = new_qty
        except ValueError:
            pass
        self.cart_table.cellChanged.disconnect(self.handle_qty_edited)
        self._refresh_cart_table()

    def handle_remove_item(self, row):
        if 0 <= row < len(self.cart):
            self.cart.pop(row)
            self._refresh_cart_table()

    def handle_clear_cart(self):
        self.cart = []
        self.diskon_input.setValue(0)
        self.uang_input.setValue(0)
        self._refresh_cart_table()

    def get_total_belanja(self):
        return sum(item["harga"] * item["jumlah"] for item in self.cart)

    def update_totals(self):
        total_belanja = self.get_total_belanja()
        diskon = self.diskon_input.value()
        total_bayar = max(total_belanja - diskon, 0)
        uang = self.uang_input.value()
        kembalian = uang - total_bayar

        self.total_label.setText(format_rupiah(total_belanja))
        self.total_bayar_label.setText(format_rupiah(total_bayar))
        self.kembalian_label.setText(format_rupiah(kembalian if kembalian > 0 else 0))

    # ---------- Pembayaran ----------
    def handle_pay(self):
        if not self.cart:
            QMessageBox.warning(self, "Keranjang Kosong", "Belum ada barang di keranjang.")
            return

        total_belanja = self.get_total_belanja()
        diskon = self.diskon_input.value()
        total_bayar = max(total_belanja - diskon, 0)
        uang = self.uang_input.value()

        if uang < total_bayar:
            QMessageBox.warning(self, "Uang Kurang", "Uang yang diterima kurang dari total bayar.")
            return

        items_payload = [{"product_id": item["product_id"], "jumlah": item["jumlah"]} for item in self.cart]

        try:
            trx = self.client.create_transaction(
                kasir_username=self.user_data["username"],
                items=items_payload,
                diskon=diskon,
                uang_diterima=uang,
            )
        except Exception as e:
            QMessageBox.critical(self, "Transaksi Gagal", str(e))
            return

        receipt_text = self._build_receipt_text(trx)
        dialog = ReceiptDialog(self, receipt_text)
        dialog.exec_()

        self.handle_clear_cart()
        self.handle_search("")

    def _build_receipt_text(self, trx: dict) -> str:
        lines = []
        lines.append("=" * 36)
        lines.append("       MINIMARKET POS".center(36))
        lines.append("=" * 36)
        lines.append(f"No: {trx['no_transaksi']}")
        lines.append(f"Kasir: {trx['kasir_username']}")
        lines.append(f"Waktu: {trx['waktu'][:19].replace('T', ' ')}")
        lines.append("-" * 36)
        for item in trx["items"]:
            lines.append(f"{item['nama_produk']}")
            lines.append(f"  {item['jumlah']} x {format_rupiah(item['harga_satuan'])} = {format_rupiah(item['subtotal'])}")
        lines.append("-" * 36)
        lines.append(f"Total Belanja: {format_rupiah(trx['total_belanja'])}")
        lines.append(f"Diskon:        {format_rupiah(trx['diskon'])}")
        lines.append(f"Total Bayar:   {format_rupiah(trx['total_bayar'])}")
        lines.append(f"Uang Diterima: {format_rupiah(trx['uang_diterima'])}")
        lines.append(f"Kembalian:     {format_rupiah(trx['kembalian'])}")
        lines.append("=" * 36)
        lines.append("  Terima kasih atas kunjungan Anda".center(36))
        lines.append("=" * 36)
        return "\n".join(lines)
