# POS Kasir Minimarket

Aplikasi kasir (Point of Sale) untuk manajemen barang seperti Indomaret/Alfamart,
dirancang untuk dipakai di **beberapa komputer kasir sekaligus** dengan data yang
otomatis tersinkron secara real-time.

## Arsitektur

```
[Komputer Server]  <-- database utama (SQLite) + API (FastAPI)
       |
       |  jaringan LAN (WiFi/kabel, satu jaringan yang sama)
       |
   +---+---+---------+
   |       |         |
[Kasir 1][Kasir 2][Kasir 3]   <- aplikasi client (.exe), tiap komputer kasir
```

- **Server**: dijalankan di 1 komputer (bisa komputer kasir utama / komputer admin
  / mini PC khusus). Menyimpan semua data produk & transaksi.
- **Client**: aplikasi desktop Windows (.exe) yang dijalankan di tiap komputer
  kasir. Semua client terhubung ke server yang sama lewat alamat IP, sehingga
  stok dan data selalu sinkron otomatis (tidak perlu proses sync manual).

## Fitur

- Login dengan role **admin** dan **kasir**
- Transaksi kasir: cari/scan barcode, keranjang belanja, diskon, hitung
  kembalian, cetak struk
- Manajemen produk (khusus admin): tambah/edit/hapus barang, kategori, harga
  beli & jual, stok, alert stok menipis
- Laporan penjualan: ringkasan harian, laporan per rentang tanggal, produk
  terlaris
- Stok otomatis berkurang setiap ada transaksi

Akun default (bisa diganti langsung di database, lihat bagian "Menambah User"):
| Username | Password  | Role  |
|----------|-----------|-------|
| admin    | admin123  | admin |
| kasir1   | kasir123  | kasir |

---

## 1. Menjalankan SERVER (di 1 komputer, jalankan sekali & biarkan menyala)

Server butuh **Python 3.10+** terinstall di komputer tersebut.

```bash
cd server
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

Setelah jalan, akan muncul tulisan `Uvicorn running on http://0.0.0.0:8000`.
**Biarkan jendela ini tetap terbuka** selama toko beroperasi — ini adalah
"otak" datanya.

### Cari tahu alamat IP komputer server
Supaya komputer kasir lain bisa connect, cari IP komputer server ini:
```bash
ipconfig
```
Cari baris **IPv4 Address**, contoh: `192.168.1.10`. Alamat server yang
dipakai di aplikasi client nanti adalah: `http://192.168.1.10:8000`

> Tips: supaya IP ini tidak berubah-ubah, atur IP Address komputer server
> jadi **Static IP** lewat Control Panel > Network > Adapter Settings.

> Firewall: kalau client tidak bisa connect, pastikan **Windows Firewall**
> di komputer server mengizinkan koneksi masuk di port 8000 (allow inbound
> rule port 8000), atau matikan sementara untuk testing.

---

## 2. Build aplikasi CLIENT menjadi .exe (di komputer Windows)

Lakukan ini di komputer Windows yang sudah install **Python 3.10+**
(tidak harus komputer server, bisa laptop developer manapun).

```
cd client
pip install -r requirements.txt
```

Lalu jalankan (double-click) file **`build_exe.bat`**, atau lewat command
prompt:
```
build_exe.bat
```

Proses ini akan menghasilkan file:
```
client\dist\POS_Kasir.exe
```

File **`POS_Kasir.exe`** inilah yang di-copy ke setiap komputer kasir.
Tidak perlu install Python di komputer kasir — file .exe ini sudah
"membawa" semuanya (self-contained), tinggal double-click untuk jalan.

### Testing dulu tanpa build .exe (opsional)
Kalau mau coba aplikasinya dulu tanpa proses build:
```
cd client
python main.py
```

---

## 3. Menjalankan aplikasi di komputer KASIR

1. Copy file `POS_Kasir.exe` ke komputer kasir (via USB / share folder / dll)
2. Double-click `POS_Kasir.exe`
3. Di layar login, isi **Alamat Server** dengan IP komputer server, contoh:
   `http://192.168.1.10:8000`
   (klik **Tes Koneksi** dulu untuk memastikan berhasil terhubung)
4. Login dengan username & password kasir
5. Alamat server ini otomatis tersimpan (file `config.json` di folder yang
   sama dengan .exe), jadi kasir tidak perlu isi ulang tiap buka aplikasi

---

## Opsi Lain: Deploy Server ke Vercel (Serverless) + Neon (Database Cloud)

Selain dijalankan di 1 komputer di jaringan LAN toko, server juga bisa
di-deploy online lewat **Vercel**, supaya komputer kasir bisa connect dari
mana saja (tidak perlu 1 jaringan WiFi yang sama) — cocok kalau nanti mau
buka banyak cabang.

Karena Vercel adalah platform *serverless* (filesystem-nya sementara/reset
tiap saat), file database SQLite **tidak bisa dipakai** di sana. Kode
server sudah disiapkan untuk otomatis pindah ke **Postgres (Neon)** kalau
environment variable `DATABASE_URL` di-set — kalau tidak di-set, tetap
fallback ke SQLite lokal seperti biasa.

### Langkah-langkah:

**1. Buat database di Neon (gratis)**
- Daftar di https://neon.tech
- Buat project baru
- Salin **connection string**-nya. Untuk serverless, pastikan pakai versi
  **pooled connection** (biasanya ada tulisan `-pooler` di hostname-nya),
  supaya tidak kehabisan slot koneksi karena banyak function berjalan
  bersamaan. Contoh formatnya:
  ```
  postgresql://user:password@ep-xxxx-pooler.region.aws.neon.tech/dbname?sslmode=require
  ```

**2. Deploy folder `server/` ke Vercel**
- Push folder `server/` ini ke repo GitHub kamu
- Buka https://vercel.com, klik **Add New Project**, pilih repo tersebut
- Vercel akan otomatis mendeteksi ini sebagai project Python/FastAPI
  (karena ada `requirements.txt` + `main.py`)

**3. Set environment variable**
- Di dashboard project Vercel: **Settings > Environment Variables**
- Tambahkan:
  - Key: `DATABASE_URL`
  - Value: connection string dari Neon (langkah 1)
- Redeploy project agar env var terbaca

**4. Selesai — dapat URL publik**
Setelah deploy berhasil, Vercel memberi URL seperti:
```
https://pos-kasir-kamu.vercel.app
```
URL inilah yang diisi di layar login aplikasi client, menggantikan
`http://192.168.x.x:8000` yang dipakai untuk mode LAN.

### Yang perlu diperhatikan (trade-off dibanding server LAN biasa):
- **Cold start**: request pertama setelah idle lama bisa terasa sedikit
  lebih lambat (function baru "bangun" dulu)
- **Perlu internet**: kalau internet toko mati, kasir tidak bisa transaksi
  sama sekali (beda dengan mode LAN yang tetap jalan walau internet mati,
  karena semua di jaringan lokal)
- **Biaya**: gratis untuk skala kecil, tapi ada limit request/bandwidth di
  paket gratis Vercel & Neon — cek dashboard masing-masing kalau transaksi
  sudah ramai

Kalau toko cuma 1 lokasi dan koneksi internetnya kadang tidak stabil, mode
**server LAN lokal** (cara awal) sebenarnya lebih aman untuk operasional
sehari-hari. Mode Vercel lebih cocok kalau sudah banyak cabang atau butuh
akses dari luar toko (misal owner mau lihat laporan dari rumah).

---

## Menambah / Mengubah User (Admin, Kasir baru, dll)

Saat ini penambahan user dilakukan langsung ke database untuk kesederhanaan.
Cara termudah: buka file `server/pos_kasir.db` pakai aplikasi seperti
**DB Browser for SQLite** (gratis, cari di Google), lalu tambah baris baru
di tabel `users`.

Kalau nanti kamu mau, saya juga bisa tambahkan halaman "Manajemen User" di
aplikasi supaya admin bisa tambah/hapus kasir langsung dari UI tanpa buka
database manual — tinggal bilang saja.

---

## Struktur Proyek

```
pos-kasir/
├── server/                 <- Jalankan di 1 komputer (server/database)
│   ├── main.py              API endpoints (FastAPI)
│   ├── models.py            Struktur tabel database
│   ├── schemas.py           Validasi data request/response
│   ├── database.py          Koneksi SQLite
│   └── requirements.txt
│
├── client/                 <- Build jadi .exe, jalankan di tiap kasir
│   ├── main.py               Entry point aplikasi
│   ├── login_window.py       Layar login
│   ├── main_window.py        Layar utama (tab-tab)
│   ├── kasir_tab.py          Layar transaksi kasir (POS)
│   ├── produk_tab.py         Layar manajemen produk (admin)
│   ├── laporan_tab.py        Layar laporan penjualan (admin)
│   ├── product_dialog.py     Form tambah/edit produk
│   ├── api_client.py         Komunikasi ke server
│   ├── config.py             Simpan alamat server
│   ├── build_exe.bat         Script build ke .exe
│   └── requirements.txt
│
└── README.md                (file ini)
```

## Pengembangan Lanjutan (ide kalau mau ditambah nanti)

- Manajemen user lewat UI (tambah/hapus kasir tanpa buka database manual)
- Cetak struk otomatis ke printer thermal (58mm/80mm) tanpa dialog print
- Barcode scanner otomatis fokus ke kolom pencarian
- Backup otomatis database ke cloud (Google Drive/Dropbox) harian
- Multi-cabang (beberapa toko dengan laporan gabungan)
- Export laporan ke Excel/PDF
- Halaman retur barang / void transaksi dengan approval admin
