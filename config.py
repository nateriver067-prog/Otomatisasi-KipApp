# config.py
import os
import json
from dotenv import load_dotenv

# ======================
# LOAD ENV
# ======================
load_dotenv()

USERNAME = os.getenv("KIPAPP_USERNAME")
PASSWORD = os.getenv("KIPAPP_PASSWORD")
NIP_LAMA = os.getenv("NIP_LAMA")

# ======================
# VALIDATOR (DIPANGGIL EXECUTOR)
# ======================
def validate_env():
    missing = []
    if not USERNAME:
        missing.append("KIPAPP_USERNAME")
    if not PASSWORD:
        missing.append("KIPAPP_PASSWORD")
    if not NIP_LAMA:
        missing.append("NIP_LAMA")

    if missing:
        raise RuntimeError(
            "ENV belum lengkap: "
            + ", ".join(missing)
            + "\nPastikan file .env ada dan terisi."
        )

# ======================
# API CONSTANT
# ======================
BASE_URL = "https://kipapp.bps.go.id/api/v1"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120 Safari/537.36"
)

# ======================
# PATH
# ======================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ======================
# LOAD CONFIG.JSON
# ======================
with open(CONFIG_PATH, encoding="utf-8") as f:
    cfg = json.load(f)

TAHUN = cfg["tahun"]
BULAN = cfg["bulan"]
NAMA_BULAN = cfg["nama_bulan"]

EXCEL_PELAKSANAAN = cfg["excel_pelaksanaan"]
SHEET_PELAKSANAAN = cfg["sheet_pelaksanaan"]
EXCEL_LINKS = cfg["excel_links"]

DELAY_POST = cfg.get("delay_post", 0.4)
ENABLE_POST_RK = cfg.get("enable_post_rk", False)

# ======================
# MUTATOR CONFIG
# ======================
def set_enable_post_rk_false():
    with open(CONFIG_PATH, "r+", encoding="utf-8") as f:
        cfg = json.load(f)
        cfg["enable_post_rk"] = False
        f.seek(0)
        json.dump(cfg, f, indent=2)
        f.truncate()
