import os
import json
from dotenv import load_dotenv

load_dotenv()

# ===== CREDENTIAL (ENV) =====
USERNAME = os.getenv("KIPAPP_USERNAME")
PASSWORD = os.getenv("KIPAPP_PASSWORD")
NIP_LAMA = os.getenv("NIP_LAMA")

if not USERNAME or not PASSWORD or not NIP_LAMA:
    raise RuntimeError("ENV belum lengkap (.env)")

# ===== PATH =====
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

# ===== PARAMETER (JSON) =====
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

def set_enable_post_rk_false():
    with open(CONFIG_PATH, "r+", encoding="utf-8") as f:
        cfg = json.load(f)
        cfg["enable_post_rk"] = False
        f.seek(0)
        json.dump(cfg, f, indent=2)
        f.truncate()
