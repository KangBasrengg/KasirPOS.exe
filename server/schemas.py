"""
Schema Pydantic: bentuk data yang masuk/keluar lewat API.
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# ---------- User / Login ----------
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    username: str
    role: str
    nama_lengkap: Optional[str] = None


# ---------- Product ----------
class ProductBase(BaseModel):
    barcode: Optional[str] = None
    nama: str
    kategori: Optional[str] = None
    harga_beli: float = 0
    harga_jual: float
    stok: int = 0
    stok_minimum: int = 5
    satuan: str = "pcs"


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    barcode: Optional[str] = None
    nama: Optional[str] = None
    kategori: Optional[str] = None
    harga_beli: Optional[float] = None
    harga_jual: Optional[float] = None
    stok: Optional[int] = None
    stok_minimum: Optional[int] = None
    satuan: Optional[str] = None


class ProductOut(ProductBase):
    id: int

    class Config:
        from_attributes = True


# ---------- Transaction ----------
class CartItem(BaseModel):
    product_id: int
    jumlah: int


class TransactionCreate(BaseModel):
    kasir_username: str
    items: List[CartItem]
    diskon: float = 0
    uang_diterima: float


class TransactionItemOut(BaseModel):
    nama_produk: str
    harga_satuan: float
    jumlah: int
    subtotal: float

    class Config:
        from_attributes = True


class TransactionOut(BaseModel):
    id: int
    no_transaksi: str
    kasir_username: str
    total_belanja: float
    diskon: float
    total_bayar: float
    uang_diterima: float
    kembalian: float
    waktu: datetime
    status: str
    items: List[TransactionItemOut] = []

    class Config:
        from_attributes = True


# ---------- Report ----------
class SalesReportItem(BaseModel):
    tanggal: str
    jumlah_transaksi: int
    total_penjualan: float


class TopProduct(BaseModel):
    nama: str
    total_terjual: int
    total_omzet: float
