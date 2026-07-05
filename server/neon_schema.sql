-- Script SQL untuk membuat tabel di Neon (PostgreSQL) secara manual
-- Jalankan script ini di SQL Editor pada dashboard Neon.tech

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL UNIQUE,
    password VARCHAR NOT NULL,
    role VARCHAR NOT NULL DEFAULT 'kasir',
    nama_lengkap VARCHAR
);
CREATE INDEX ix_users_username ON users (username);
CREATE INDEX ix_users_id ON users (id);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    barcode VARCHAR UNIQUE,
    nama VARCHAR NOT NULL,
    kategori VARCHAR,
    harga_beli FLOAT DEFAULT 0,
    harga_jual FLOAT NOT NULL,
    stok INTEGER DEFAULT 0,
    stok_minimum INTEGER DEFAULT 5,
    satuan VARCHAR DEFAULT 'pcs'
);
CREATE INDEX ix_products_barcode ON products (barcode);
CREATE INDEX ix_products_id ON products (id);

CREATE TABLE transactions (
    id SERIAL PRIMARY KEY,
    no_transaksi VARCHAR UNIQUE,
    kasir_username VARCHAR NOT NULL,
    total_belanja FLOAT NOT NULL,
    diskon FLOAT DEFAULT 0,
    total_bayar FLOAT NOT NULL,
    uang_diterima FLOAT NOT NULL,
    kembalian FLOAT DEFAULT 0,
    waktu TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR DEFAULT 'selesai'
);
CREATE INDEX ix_transactions_no_transaksi ON transactions (no_transaksi);
CREATE INDEX ix_transactions_id ON transactions (id);

CREATE TABLE transaction_items (
    id SERIAL PRIMARY KEY,
    transaction_id INTEGER REFERENCES transactions(id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES products(id) ON DELETE SET NULL,
    nama_produk VARCHAR NOT NULL,
    harga_satuan FLOAT NOT NULL,
    jumlah INTEGER NOT NULL,
    subtotal FLOAT NOT NULL
);
CREATE INDEX ix_transaction_items_id ON transaction_items (id);

-- Insert data admin dan kasir default
INSERT INTO users (username, password, role, nama_lengkap) 
VALUES 
('admin', 'admin123', 'admin', 'Administrator'),
('kasir1', 'kasir123', 'kasir', 'Kasir 1');
