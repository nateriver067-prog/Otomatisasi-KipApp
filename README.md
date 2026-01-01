# KipApp Automation CLI (v1.2)

Automasi pengelolaan **SKP Bulanan KipApp (BPS)** berbasis **Python + CLI**.

Project ini dirancang agar **pegawai cukup mengisi Excel**, lalu seluruh proses:
- Scraping data RK Tahunan (RK + IKI)
- Scraping presensi / pelaksanaan harian
- Generate folder & share link Google Drive (1 tanggal = 1 folder = 1 link)
- Aktivasi RK Bulanan (one-time, aman)
- Post Pelaksanaan harian

bisa dijalankan **otomatis, aman, dan terkontrol** melalui Command Line Interface.

---

## ✨ Fitur Utama

- Scraping Rencana Kinerja Tahunan (RK + IKI)
- Scraping Presensi / Pelaksanaan harian
- Generate folder & share link Drive otomatis
- Aktivasi RK Bulanan (one-time safety)
- Post Pelaksanaan otomatis
- Mode **DRY RUN** (simulasi tanpa POST ke server)
- Retry & delay aman (anti request robotik)
- CLI Tool (siap clone & jalan di PC pegawai lain)

---

## 🧩 Prasyarat Sistem

### 1. Python

Project ini membutuhkan:
- **Python versi 3.9 atau lebih baru**
- Disarankan: **Python 3.10**

Cek versi Python:
```bash
python --version
```

Jika belum ada Python, install dari:
👉 https://www.python.org/downloads/

⚠️ **Windows**: pastikan mencentang **Add Python to PATH** saat instalasi.

---

### 2. pip (Python Package Manager)

Biasanya sudah otomatis terpasang bersama Python.

Cek pip:
```bash
pip --version
```

Jika belum tersedia:
```bash
python -m ensurepip --upgrade
```

---

### 3. Install Dependency

Clone repository lalu install dependency:
```bash
git clone <repo-url>
cd Otomatisasi-KipApp
pip install -r requirements.txt
```

Isi `requirements.txt`:
- selenium
- webdriver-manager
- requests
- pandas
- tqdm
- python-dotenv
- xlsxwriter

---

### 4. (Opsional tapi Disarankan) Virtual Environment

```bash
python -m venv venv
venv\\Scripts\\activate   # Windows
pip install -r requirements.txt
```

---

## 📂 Struktur Project

```
KipApp/
├── kipapp.py              # CLI entry point
├── auth/
│   ├── kipapp.py          # Login KipApp (X-Auth)
│   └── drive.py           # Auth Google Drive
├── api/
│   ├── skp.py             # API KipApp (SKP, RK, Pelaksanaan)
│   ├── kegiatan.py        # API POST kegiatan
│   └── drive.py           # API Drive
├── parser/
│   ├── rk_parser.py       # Parser RK + IKI
│   └── pelaksanaan_parser.py
├── executor/
│   ├── scrap.py           # Scraping data
│   ├── post_rk.py         # Aktivasi RK Bulanan
│   ├── generate_drive_links.py
│   └── post_pelaksanaan.py
├── config.py              # Loader env + config.json
├── utils.py               # Retry, delay, helper
├── logger.py              # Logging
├── .env.example           # Contoh ENV (AMAN)
├── config.json            # Konfigurasi kerja
├── output/                # Output Excel & link (ignored)
└── README.md
```

---

## ⚙️ Konfigurasi

### 1. File `.env` (WAJIB, jangan di-commit)

Buat file `.env` berdasarkan `.env.example`:

```
KIPAPP_USERNAME=nama.user
KIPAPP_PASSWORD=password
NIP_LAMA=xxxxxxxxx
```

---

### 2. File `config.json`

Mengatur:
- tahun & bulan kerja
- enable_post_rk (one-time safety)
- opsi perilaku automation

---

## 🚀 Cara Pakai

### 1. Scraping Data
```bash
python kipapp.py scrap
```

### 2. Aktivasi RK Bulanan (sekali per bulan)
```bash
python kipapp.py post-rk --dry-run
python kipapp.py post-rk
```

### 3. Generate Link Drive
```bash
python kipapp.py gen-links --dry-run
python kipapp.py gen-links
```

### 4. Post Pelaksanaan
```bash
python kipapp.py post --dry-run
python kipapp.py post
```

### 5. Jalankan Semua Tahapan
```bash
python kipapp.py all --dry-run
python kipapp.py all
```

---

## 🔐 Keamanan & Etika Automation

- File `.env` tidak masuk Git
- DRY RUN tidak mengirim request ke server
- Retry selektif (429 / 5xx)
- Delay acak (anti pola bot)
- Validasi RK, tanggal, dan link Drive sebelum POST
- Infrastruktur SAFE MODE siap (belum aktif default)

---

## 🏷️ Versi

- **v1.2** – Throttling-ready, retry & jitter delay, arsitektur CLI stabil

---

## 🛣️ Roadmap

### v1.3
- Flag `--safe` (SAFE MODE)
- Hard limit jumlah POST per run
- Logging mode eksekusi (normal / safe)

### v1.4
- Resume mode (skip data yang sudah sukses)
- Summary statistik waktu eksekusi

### v2.0
- Installer / packaged CLI (non-developer friendly)
- Multi-user readiness
- Config wizard (interactive)

---

Internal automation – KipApp BPS
