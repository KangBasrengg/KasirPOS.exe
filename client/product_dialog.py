"""
Dialog untuk tambah / edit produk.
"""
from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QDoubleSpinBox, QSpinBox,
    QPushButton, QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt


class ProductDialog(QDialog):
    def __init__(self, parent=None, product: dict = None):
        super().__init__(parent)
        self.product = product  # None = mode tambah, dict = mode edit
        self.setWindowTitle("Edit Produk" if product else "Tambah Produk")
        self.setMinimumWidth(400)
        self._build_ui()
        if product:
            self._fill_data(product)

    def _build_ui(self):
        layout = QFormLayout()
        layout.setSpacing(10)

        self.barcode_input = QLineEdit()
        self.barcode_input.setMinimumHeight(34)
        self.nama_input = QLineEdit()
        self.nama_input.setMinimumHeight(34)
        self.kategori_input = QLineEdit()
        self.kategori_input.setMinimumHeight(34)

        self.harga_beli_input = QDoubleSpinBox()
        self.harga_beli_input.setMaximum(999999999)
        self.harga_beli_input.setDecimals(0)
        self.harga_beli_input.setMinimumHeight(34)

        self.harga_jual_input = QDoubleSpinBox()
        self.harga_jual_input.setMaximum(999999999)
        self.harga_jual_input.setDecimals(0)
        self.harga_jual_input.setMinimumHeight(34)

        self.stok_input = QSpinBox()
        self.stok_input.setMaximum(999999)
        self.stok_input.setMinimumHeight(34)

        self.stok_min_input = QSpinBox()
        self.stok_min_input.setMaximum(999999)
        self.stok_min_input.setValue(5)
        self.stok_min_input.setMinimumHeight(34)

        self.satuan_input = QLineEdit()
        self.satuan_input.setText("pcs")
        self.satuan_input.setMinimumHeight(34)

        layout.addRow("Barcode:", self.barcode_input)
        layout.addRow("Nama Produk*:", self.nama_input)
        layout.addRow("Kategori:", self.kategori_input)
        layout.addRow("Harga Beli:", self.harga_beli_input)
        layout.addRow("Harga Jual*:", self.harga_jual_input)
        layout.addRow("Stok:", self.stok_input)
        layout.addRow("Stok Minimum:", self.stok_min_input)
        layout.addRow("Satuan:", self.satuan_input)

        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Simpan")
        self.save_btn.setObjectName("btn_success")
        self.save_btn.setMinimumHeight(38)
        self.save_btn.setCursor(Qt.PointingHandCursor)
        self.save_btn.clicked.connect(self._handle_save)

        self.cancel_btn = QPushButton("Batal")
        self.cancel_btn.setMinimumHeight(38)
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addRow(btn_layout)

        self.setLayout(layout)

    def _fill_data(self, product: dict):
        self.barcode_input.setText(product.get("barcode") or "")
        self.nama_input.setText(product.get("nama") or "")
        self.kategori_input.setText(product.get("kategori") or "")
        self.harga_beli_input.setValue(product.get("harga_beli") or 0)
        self.harga_jual_input.setValue(product.get("harga_jual") or 0)
        self.stok_input.setValue(product.get("stok") or 0)
        self.stok_min_input.setValue(product.get("stok_minimum") or 5)
        self.satuan_input.setText(product.get("satuan") or "pcs")

    def _handle_save(self):
        if not self.nama_input.text().strip():
            QMessageBox.warning(self, "Peringatan", "Nama produk harus diisi.")
            return
        if self.harga_jual_input.value() <= 0:
            QMessageBox.warning(self, "Peringatan", "Harga jual harus lebih dari 0.")
            return
        self.accept()

    def get_data(self) -> dict:
        return {
            "barcode": self.barcode_input.text().strip() or None,
            "nama": self.nama_input.text().strip(),
            "kategori": self.kategori_input.text().strip() or None,
            "harga_beli": self.harga_beli_input.value(),
            "harga_jual": self.harga_jual_input.value(),
            "stok": self.stok_input.value(),
            "stok_minimum": self.stok_min_input.value(),
            "satuan": self.satuan_input.text().strip() or "pcs",
        }
