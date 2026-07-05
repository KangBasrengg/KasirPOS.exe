"""
Tab Manajemen Produk (khusus admin): tambah, edit, hapus barang, cek stok menipis.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt


def format_rupiah(value):
    return f"Rp {value:,.0f}".replace(",", ".")


class ProdukTab(QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self._current_products = []
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        top_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari nama produk atau barcode...")
        self.search_input.setMinimumHeight(36)
        self.search_input.textChanged.connect(self.refresh_table)
        top_row.addWidget(self.search_input)

        add_btn = QPushButton("+ Tambah Produk")
        add_btn.setObjectName("btn_primary")
        add_btn.setMinimumHeight(36)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.handle_add)
        top_row.addWidget(add_btn)

        low_stock_btn = QPushButton("Lihat Stok Menipis")
        low_stock_btn.setMinimumHeight(36)
        low_stock_btn.setCursor(Qt.PointingHandCursor)
        low_stock_btn.clicked.connect(self.handle_show_low_stock)
        top_row.addWidget(low_stock_btn)
        layout.addLayout(top_row)

        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(["Nama", "Kategori", "Barcode", "Harga Beli", "Harga Jual", "Stok", "Aksi"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)
        self.setLayout(layout)
        self.refresh_table()

    def refresh_table(self):
        keyword = self.search_input.text().strip()
        try:
            products = self.client.list_products(search=keyword)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengambil data produk:\n{e}")
            return
        self._render_table(products)

    def _render_table(self, products):
        self._current_products = products
        self.table.setRowCount(0)
        for row, p in enumerate(products):
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(p["nama"]))
            self.table.setItem(row, 1, QTableWidgetItem(p.get("kategori") or "-"))
            self.table.setItem(row, 2, QTableWidgetItem(p.get("barcode") or "-"))
            self.table.setItem(row, 3, QTableWidgetItem(format_rupiah(p["harga_beli"])))
            self.table.setItem(row, 4, QTableWidgetItem(format_rupiah(p["harga_jual"])))
            self.table.setItem(row, 5, QTableWidgetItem(str(p["stok"])))

            action_widget = QWidget()
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(4, 2, 4, 2)
            edit_btn = QPushButton("Edit")
            edit_btn.setObjectName("btn_primary")
            edit_btn.setCursor(Qt.PointingHandCursor)
            edit_btn.clicked.connect(lambda checked, prod=p: self.handle_edit(prod))
            delete_btn = QPushButton("Hapus")
            delete_btn.setObjectName("btn_danger")
            delete_btn.setCursor(Qt.PointingHandCursor)
            delete_btn.clicked.connect(lambda checked, prod=p: self.handle_delete(prod))
            action_layout.addWidget(edit_btn)
            action_layout.addWidget(delete_btn)
            action_widget.setLayout(action_layout)
            self.table.setCellWidget(row, 6, action_widget)

    def handle_add(self):
        from product_dialog import ProductDialog
        dialog = ProductDialog(self)
        if dialog.exec_():
            data = dialog.get_data()
            try:
                self.client.create_product(data)
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Gagal", str(e))

    def handle_edit(self, product):
        from product_dialog import ProductDialog
        dialog = ProductDialog(self, product)
        if dialog.exec_():
            data = dialog.get_data()
            try:
                self.client.update_product(product["id"], data)
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Gagal", str(e))

    def handle_delete(self, product):
        confirm = QMessageBox.question(
            self, "Konfirmasi", f"Yakin hapus produk '{product['nama']}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm == QMessageBox.Yes:
            try:
                self.client.delete_product(product["id"])
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Gagal", str(e))

    def handle_show_low_stock(self):
        try:
            products = self.client.low_stock_products()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengambil data:\n{e}")
            return
        if not products:
            QMessageBox.information(self, "Info", "Tidak ada produk dengan stok menipis.")
            return
        self.search_input.clear()
        self._render_table(products)
