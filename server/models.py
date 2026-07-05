"""
Model / tabel database untuk aplikasi POS.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class User(Base):
    """Akun untuk login (admin / kasir)"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)  # disimpan hash di produksi nyata
    role = Column(String, nullable=False, default="kasir")  # "admin" atau "kasir"
    nama_lengkap = Column(String, nullable=True)


class Product(Base):
    """Data barang / produk"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    barcode = Column(String, unique=True, index=True, nullable=True)
    nama = Column(String, nullable=False)
    kategori = Column(String, nullable=True)
    harga_beli = Column(Float, default=0)
    harga_jual = Column(Float, nullable=False)
    stok = Column(Integer, default=0)
    stok_minimum = Column(Integer, default=5)  # untuk alert stok menipis
    satuan = Column(String, default="pcs")  # pcs, kg, dus, dll


class Transaction(Base):
    """Header transaksi penjualan"""
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    no_transaksi = Column(String, unique=True, index=True)
    kasir_username = Column(String, nullable=False)
    total_belanja = Column(Float, nullable=False)
    diskon = Column(Float, default=0)
    total_bayar = Column(Float, nullable=False)
    uang_diterima = Column(Float, nullable=False)
    kembalian = Column(Float, default=0)
    waktu = Column(DateTime, default=datetime.now)
    status = Column(String, default="selesai")  # selesai / void

    items = relationship("TransactionItem", back_populates="transaction", cascade="all, delete-orphan")


class TransactionItem(Base):
    """Detail barang yang dibeli dalam satu transaksi"""
    __tablename__ = "transaction_items"

    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(Integer, ForeignKey("transactions.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    nama_produk = Column(String, nullable=False)  # disalin agar histori tetap utuh walau produk dihapus/diubah
    harga_satuan = Column(Float, nullable=False)
    jumlah = Column(Integer, nullable=False)
    subtotal = Column(Float, nullable=False)

    transaction = relationship("Transaction", back_populates="items")
