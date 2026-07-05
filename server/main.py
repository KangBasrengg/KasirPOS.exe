"""
Server POS Kasir - FastAPI
==========================
Jalankan dengan:
    uvicorn main:app --host 0.0.0.0 --port 8000

Semua komputer kasir (client) akan connect ke IP komputer ini di port 8000.
Contoh: http://192.168.1.10:8000
"""
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from typing import List
import uuid

from database import Base, engine, get_db
import models
import schemas

# Buat semua tabel jika belum ada
Base.metadata.create_all(bind=engine)

app = FastAPI(title="POS Kasir Server", version="1.0")

# Izinkan diakses dari aplikasi client di komputer manapun dalam jaringan
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def seed_default_admin(db: Session):
    """Buat akun admin default kalau belum ada user sama sekali"""
    if db.query(models.User).count() == 0:
        admin = models.User(username="admin", password="admin123", role="admin", nama_lengkap="Administrator")
        kasir = models.User(username="kasir1", password="kasir123", role="kasir", nama_lengkap="Kasir 1")
        db.add_all([admin, kasir])
        db.commit()


@app.on_event("startup")
def on_startup():
    db = next(get_db())
    seed_default_admin(db)


@app.get("/")
def root():
    return {"status": "ok", "message": "POS Kasir Server berjalan"}


# ==================== LOGIN ====================
@app.post("/login", response_model=schemas.LoginResponse)
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.username == data.username,
        models.User.password == data.password
    ).first()
    if not user:
        raise HTTPException(status_code=401, detail="Username atau password salah")
    return schemas.LoginResponse(username=user.username, role=user.role, nama_lengkap=user.nama_lengkap)


# ==================== PRODUK ====================
@app.get("/products", response_model=List[schemas.ProductOut])
def list_products(search: str = "", db: Session = Depends(get_db)):
    q = db.query(models.Product)
    if search:
        like = f"%{search}%"
        q = q.filter((models.Product.nama.ilike(like)) | (models.Product.barcode.ilike(like)))
    return q.order_by(models.Product.nama).all()


@app.get("/products/barcode/{barcode}", response_model=schemas.ProductOut)
def get_product_by_barcode(barcode: str, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.barcode == barcode).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    return product


@app.post("/products", response_model=schemas.ProductOut)
def create_product(data: schemas.ProductCreate, db: Session = Depends(get_db)):
    if data.barcode:
        existing = db.query(models.Product).filter(models.Product.barcode == data.barcode).first()
        if existing:
            raise HTTPException(status_code=400, detail="Barcode sudah dipakai produk lain")
    product = models.Product(**data.dict())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@app.put("/products/{product_id}", response_model=schemas.ProductOut)
def update_product(product_id: int, data: schemas.ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    for field, value in data.dict(exclude_unset=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product


@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produk tidak ditemukan")
    db.delete(product)
    db.commit()
    return {"message": "Produk dihapus"}


@app.get("/products/low-stock/list", response_model=List[schemas.ProductOut])
def low_stock_products(db: Session = Depends(get_db)):
    """List produk yang stoknya di bawah atau sama dengan stok minimum"""
    products = db.query(models.Product).all()
    return [p for p in products if p.stok <= p.stok_minimum]


# ==================== TRANSAKSI ====================
@app.post("/transactions", response_model=schemas.TransactionOut)
def create_transaction(data: schemas.TransactionCreate, db: Session = Depends(get_db)):
    if not data.items:
        raise HTTPException(status_code=400, detail="Keranjang belanja kosong")

    total_belanja = 0
    trx_items = []

    # Validasi stok & hitung total dulu sebelum simpan apapun
    for item in data.items:
        product = db.query(models.Product).filter(models.Product.id == item.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Produk id {item.product_id} tidak ditemukan")
        if product.stok < item.jumlah:
            raise HTTPException(status_code=400, detail=f"Stok '{product.nama}' tidak cukup (sisa {product.stok})")
        subtotal = product.harga_jual * item.jumlah
        total_belanja += subtotal
        trx_items.append((product, item.jumlah, subtotal))

    total_bayar = total_belanja - data.diskon
    if total_bayar < 0:
        total_bayar = 0

    if data.uang_diterima < total_bayar:
        raise HTTPException(status_code=400, detail="Uang yang diterima kurang dari total bayar")

    kembalian = data.uang_diterima - total_bayar
    no_transaksi = f"TRX-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:4].upper()}"

    trx = models.Transaction(
        no_transaksi=no_transaksi,
        kasir_username=data.kasir_username,
        total_belanja=total_belanja,
        diskon=data.diskon,
        total_bayar=total_bayar,
        uang_diterima=data.uang_diterima,
        kembalian=kembalian,
    )
    db.add(trx)
    db.flush()  # supaya trx.id tersedia

    for product, jumlah, subtotal in trx_items:
        db.add(models.TransactionItem(
            transaction_id=trx.id,
            product_id=product.id,
            nama_produk=product.nama,
            harga_satuan=product.harga_jual,
            jumlah=jumlah,
            subtotal=subtotal,
        ))
        product.stok -= jumlah  # kurangi stok

    db.commit()
    db.refresh(trx)
    return trx


@app.get("/transactions", response_model=List[schemas.TransactionOut])
def list_transactions(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(models.Transaction).order_by(models.Transaction.waktu.desc()).limit(limit).all()


@app.get("/transactions/{trx_id}", response_model=schemas.TransactionOut)
def get_transaction(trx_id: int, db: Session = Depends(get_db)):
    trx = db.query(models.Transaction).filter(models.Transaction.id == trx_id).first()
    if not trx:
        raise HTTPException(status_code=404, detail="Transaksi tidak ditemukan")
    return trx


# ==================== LAPORAN ====================
@app.get("/reports/sales-today")
def sales_today(db: Session = Depends(get_db)):
    today = date.today()
    trxs = db.query(models.Transaction).filter(
        func.date(models.Transaction.waktu) == str(today)
    ).all()
    total = sum(t.total_bayar for t in trxs)
    return {
        "tanggal": str(today),
        "jumlah_transaksi": len(trxs),
        "total_penjualan": total,
    }


@app.get("/reports/sales-range", response_model=List[schemas.SalesReportItem])
def sales_range(start_date: str, end_date: str, db: Session = Depends(get_db)):
    """Format tanggal: YYYY-MM-DD"""
    trxs = db.query(models.Transaction).filter(
        func.date(models.Transaction.waktu) >= start_date,
        func.date(models.Transaction.waktu) <= end_date,
    ).all()

    grouped = {}
    for t in trxs:
        tgl = t.waktu.strftime("%Y-%m-%d")
        if tgl not in grouped:
            grouped[tgl] = {"jumlah": 0, "total": 0}
        grouped[tgl]["jumlah"] += 1
        grouped[tgl]["total"] += t.total_bayar

    result = [
        schemas.SalesReportItem(tanggal=tgl, jumlah_transaksi=v["jumlah"], total_penjualan=v["total"])
        for tgl, v in sorted(grouped.items())
    ]
    return result


@app.get("/reports/top-products", response_model=List[schemas.TopProduct])
def top_products(limit: int = 10, db: Session = Depends(get_db)):
    items = db.query(models.TransactionItem).all()
    grouped = {}
    for i in items:
        if i.nama_produk not in grouped:
            grouped[i.nama_produk] = {"jumlah": 0, "omzet": 0}
        grouped[i.nama_produk]["jumlah"] += i.jumlah
        grouped[i.nama_produk]["omzet"] += i.subtotal

    result = [
        schemas.TopProduct(nama=nama, total_terjual=v["jumlah"], total_omzet=v["omzet"])
        for nama, v in grouped.items()
    ]
    result.sort(key=lambda x: x.total_terjual, reverse=True)
    return result[:limit]
