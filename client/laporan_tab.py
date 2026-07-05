"""
Tab Laporan: ringkasan penjualan hari ini, produk terlaris, dan laporan rentang tanggal.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QDateEdit, QGroupBox
)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont

from themes import get_theme
from config import load_config


def format_rupiah(value):
    return f"Rp {value:,.0f}".replace(",", ".")


class LaporanTab(QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        config = load_config()
        self._theme = get_theme(config.get("theme", "dark"))
        self._build_ui()
        self.refresh_summary()

    def _build_ui(self):
        layout = QVBoxLayout()

        # ---- Ringkasan hari ini ----
        summary_box = QGroupBox("Ringkasan Penjualan Hari Ini")
        summary_layout = QHBoxLayout()

        self.jumlah_trx_label = QLabel("0")
        self.jumlah_trx_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.total_penjualan_label = QLabel("Rp 0")
        self.total_penjualan_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.total_penjualan_label.setStyleSheet(f"color:{self._theme['accent_green']};")

        col1 = QVBoxLayout()
        col1.addWidget(QLabel("Jumlah Transaksi"))
        col1.addWidget(self.jumlah_trx_label)
        col2 = QVBoxLayout()
        col2.addWidget(QLabel("Total Penjualan"))
        col2.addWidget(self.total_penjualan_label)

        summary_layout.addLayout(col1)
        summary_layout.addLayout(col2)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("btn_primary")
        refresh_btn.setMinimumHeight(36)
        refresh_btn.setCursor(Qt.PointingHandCursor)
        refresh_btn.clicked.connect(self.refresh_summary)
        summary_layout.addWidget(refresh_btn)

        summary_box.setLayout(summary_layout)
        layout.addWidget(summary_box)

        # ---- Laporan rentang tanggal ----
        range_box = QGroupBox("Laporan Penjualan per Rentang Tanggal")
        range_layout = QVBoxLayout()

        date_row = QHBoxLayout()
        date_row.addWidget(QLabel("Dari:"))
        self.start_date = QDateEdit(calendarPopup=True)
        self.start_date.setDate(QDate.currentDate().addDays(-7))
        self.start_date.setMinimumHeight(34)
        date_row.addWidget(self.start_date)

        date_row.addWidget(QLabel("Sampai:"))
        self.end_date = QDateEdit(calendarPopup=True)
        self.end_date.setDate(QDate.currentDate())
        self.end_date.setMinimumHeight(34)
        date_row.addWidget(self.end_date)

        show_btn = QPushButton("Tampilkan")
        show_btn.setObjectName("btn_primary")
        show_btn.setMinimumHeight(36)
        show_btn.setCursor(Qt.PointingHandCursor)
        show_btn.clicked.connect(self.handle_show_range_report)
        date_row.addWidget(show_btn)

        range_layout.addLayout(date_row)

        self.range_table = QTableWidget(0, 3)
        self.range_table.setHorizontalHeaderLabels(["Tanggal", "Jumlah Transaksi", "Total Penjualan"])
        self.range_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.range_table.setAlternatingRowColors(True)
        range_layout.addWidget(self.range_table)

        range_box.setLayout(range_layout)
        layout.addWidget(range_box)

        # ---- Produk terlaris ----
        top_box = QGroupBox("Produk Terlaris")
        top_layout = QVBoxLayout()
        self.top_table = QTableWidget(0, 3)
        self.top_table.setHorizontalHeaderLabels(["Nama Produk", "Total Terjual", "Total Omzet"])
        self.top_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.top_table.setAlternatingRowColors(True)
        top_layout.addWidget(self.top_table)
        top_box.setLayout(top_layout)
        layout.addWidget(top_box)

        self.setLayout(layout)

    def refresh_summary(self):
        try:
            data = self.client.sales_today()
            self.jumlah_trx_label.setText(str(data["jumlah_transaksi"]))
            self.total_penjualan_label.setText(format_rupiah(data["total_penjualan"]))

            top_products = self.client.top_products(limit=10)
            self.top_table.setRowCount(0)
            for row, p in enumerate(top_products):
                self.top_table.insertRow(row)
                self.top_table.setItem(row, 0, QTableWidgetItem(p["nama"]))
                self.top_table.setItem(row, 1, QTableWidgetItem(str(p["total_terjual"])))
                self.top_table.setItem(row, 2, QTableWidgetItem(format_rupiah(p["total_omzet"])))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengambil laporan:\n{e}")

    def handle_show_range_report(self):
        start = self.start_date.date().toString("yyyy-MM-dd")
        end = self.end_date.date().toString("yyyy-MM-dd")
        try:
            report = self.client.sales_range(start, end)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Gagal mengambil laporan:\n{e}")
            return

        self.range_table.setRowCount(0)
        for row, r in enumerate(report):
            self.range_table.insertRow(row)
            self.range_table.setItem(row, 0, QTableWidgetItem(r["tanggal"]))
            self.range_table.setItem(row, 1, QTableWidgetItem(str(r["jumlah_transaksi"])))
            self.range_table.setItem(row, 2, QTableWidgetItem(format_rupiah(r["total_penjualan"])))

        if not report:
            QMessageBox.information(self, "Info", "Tidak ada transaksi pada rentang tanggal tersebut.")
