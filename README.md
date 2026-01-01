# KipApp Automation CLI (v1)

Automasi pengelolaan **SKP Bulanan KipApp (BPS)** berbasis Python + CLI.

Project ini dirancang agar **pegawai cukup mengisi Excel**, lalu seluruh proses:
- Scraping data RK & presensi
- Generate folder & link Drive
- Aktivasi RK Bulanan (one-time)
- Post Pelaksanaan harian

bisa dijalankan **otomatis, aman, dan terkontrol**.

---

## ✨ Fitur Utama

- Scraping Rencana Kinerja Tahunan (RK + IKI) dan Presensi / Pelaksanaan harian
- Generate folder & share link Drive (1 link per tanggal)
- Aktivasi RK Bulanan (one-time, aman)
- Post Pelaksanaan otomatis
- Mode DRY RUN (simulasi tanpa POST)
- CLI Tool (siap clone & jalan di PC pegawai lain)

---

## 📂 Struktur Project

KipApp/
├── kipapp.py              # CLI entry point
├── auth/
│   └── kipapp.py          # Login SSO KipApp (X-Auth)
├── api/
│   ├── skp.py             # API KipApp (SKP, RK, Pelaksanaan)
│   └── drive.py           # API Drive BPS
├── parser/
│   ├── rk_parser.py       # Parser RK + IKI
│   └── pelaksanaan_parser.py
├── executor/
│   ├── scrap.py           # Scraping RK & Pelaksanaan
│   ├── post_rk.py         # Aktivasi RK Bulanan
│   ├── generate_drive_links.py
│   └── post_pelaksanaan.py
├── config.py              # Loader env + config.json
├── utils.py               # HTTP retry & helper
├── logger.py              # Logging
├── .env.example           # Contoh ENV (AMAN)
├── config.json            # Konfigurasi kerja
├── output/                # Output Excel & link
└── README.md

---

## ⚙️ Konfigurasi

### 1. File `.env` (jangan di-commit)

Buat file `.env` berdasarkan `.env.example`:

KIPAPP_USERNAME=nama.user  
KIPAPP_PASSWORD=password  
NIP_LAMA=xxxxxxxxx  

### 2. File `config.json`

Atur tahun, bulan, dan opsi kerja:

- enable_post_rk = true → RK Bulanan boleh dipost
- otomatis menjadi false setelah sukses (one-time safety)

---

## 🚀 Cara Pakai

### 1. Scraping Data
python kipapp.py scrap

### 2. Aktivasi RK Bulanan (sekali per bulan)
python kipapp.py post-rk --dry-run  
python kipapp.py post-rk

### 3. Generate Link Drive
python kipapp.py gen-links --dry-run  
python kipapp.py gen-links

### 4. Post Pelaksanaan
python kipapp.py post --dry-run  
python kipapp.py post

### 5. Jalankan Semua
python kipapp.py all --dry-run  
python kipapp.py all

---

## 🔐 Keamanan

- File `.env` tidak masuk Git
- RK Bulanan tidak bisa double-post
- Validasi RK, tanggal, dan link Drive sebelum POST

---

## 🏷️ Versi

v1.0 – Stabil & siap produksi

---

Internal automation – BPS KipApp
