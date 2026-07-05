"""
Koneksi database untuk server POS.

- Kalau environment variable DATABASE_URL di-set (misalnya connection string
  Postgres dari Neon), server akan pakai itu -> cocok untuk deploy serverless
  di Vercel (karena Vercel tidak punya filesystem permanen untuk SQLite).
- Kalau tidak di-set, otomatis fallback ke file SQLite lokal -> cocok untuk
  development / testing di komputer sendiri, atau kalau tetap mau pakai
  model 1 server fisik di jaringan LAN toko.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./pos_kasir.db")

# Neon (dan beberapa provider lain) kadang memberi connection string dengan
# awalan "postgres://", padahal SQLAlchemy versi baru butuh "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# check_same_thread hanya relevan untuk SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# pool_pre_ping: cek koneksi masih hidup sebelum dipakai -> penting untuk
# serverless karena koneksi ke database bisa idle lama antar request
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
