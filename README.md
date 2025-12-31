# KipApp Automation CLI

Tool otomatisasi internal untuk:
- Scraping data KipApp (RK & Pelaksanaan)
- Generate folder & link Drive BPS
- Post RK Bulanan
- Post Pelaksanaan Harian

Dirancang aman, modular, dan bisa digunakan ulang oleh pegawai lain
dengan cara clone repository.

---

## 📁 Struktur Project

KipApp/
│
├── kipapp.py # CLI entry point
│
├── auth/ # Login & auth (SSO)
├── api/ # Wrapper API KipApp & Drive
├── parser/ # Parser → DataFrame
├── executor/ # Logic utama (scrap / post / drive)
│
├── config.py # Loader .env & config.json
├── utils.py # Retry, error handling
├── logger.py # Logging terpusat
│
├── .env # RAHASIA (tidak di-commit)
├── .env.example # Contoh env
├── config.json # Parameter kerja
│
├── output/ # Hasil Excel & log
└── README.md

yaml
Salin kode

---

## ⚙️ Persiapan Awal

### 1️⃣ Clone repository
```bash
git clone <repo-url>
cd KipApp
2️⃣ Buat virtual environment (disarankan)
bash
Salin kode
python -m venv .venv
source .venv/bin/activate   # Linux / Mac
.venv\Scripts\activate      # Windows
3️⃣ Install dependency
bash
Salin kode
pip install -r requirements.txt

🔐 Konfigurasi Environment
.env
Buat file .env berdasarkan .env.example:
.env
Salin kode
KIPAPP_USERNAME="Username Anda"
KIPAPP_PASSWORD="Password Anda"
NIP_LAMA="NIP 9 Anda"

config.json
Contoh:

json
Salin kode
{
  "tahun": 2025,
  "bulan": 12,
  "nama_bulan": "Desember",

  "excel_pelaksanaan": "output/KipApp_Pelaksanaan_dan_RK.xlsx",
  "sheet_pelaksanaan": "Pelaksanaan",
  "excel_links": "output/KipApp_2025_12_links.xlsx",

  "delay_post": 0.4,
  "enable_post_rk": true
}
🚀 Cara Pakai (CLI)
1️⃣ Scraping data
bash
Salin kode
python kipapp.py scrap
Menghasilkan:

output/KipApp_Pelaksanaan_dan_RK.xlsx

2️⃣ Post RK Bulanan
bash
Salin kode
python kipapp.py post-rk
🔐 Hanya dijalankan 1x per bulan
Setelah sukses → otomatis enable_post_rk = false

Dry run:

bash
Salin kode
python kipapp.py post-rk --dry-run
3️⃣ Generate Drive Links
bash
Salin kode
python kipapp.py gen-links
Struktur Drive:

css
Salin kode
KipApp/YYYY/MM/YYYY-MM-DD
Dry run:

bash
Salin kode
python kipapp.py gen-links --dry-run
4️⃣ Post Pelaksanaan
bash
Salin kode
python kipapp.py post
Dry run:

bash
Salin kode
python kipapp.py post --dry-run
5️⃣ Full Pipeline
bash
Salin kode
python kipapp.py all
Dry run aman:

bash
Salin kode
python kipapp.py all --dry-run
🧪 DRY RUN MODE
Jika --dry-run aktif:

❌ Tidak ada POST ke KipApp

❌ Tidak membuat folder / link Drive

✅ Validasi data & mapping tetap berjalan

Sangat disarankan sebelum REAL RUN.

⚠️ Catatan Penting
RKID & Rencana Kinerja

RKID di Excel diisi otomatis (XLOOKUP)

Validasi rkid.isdigit() sudah aktif

Duplicate Protection

Pelaksanaan yang sudah ada tidak akan di-post ulang

Drive link: 1 folder = 1 link (tidak duplikat)

Keamanan

Jangan commit .env

Gunakan akun masing-masing

