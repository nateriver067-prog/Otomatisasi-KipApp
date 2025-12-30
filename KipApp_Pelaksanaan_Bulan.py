import time
import json
import requests
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# =========================
# KONFIGURASI USER
# =========================
USERNAME = "iqbal.m"
PASSWORD = "Tokyoghoul123"
NIP_LAMA = "340060186"

BASE_URL = "https://kipapp.bps.go.id/api/v1"

# =========================
# LOGIN SSO + AMBIL X-AUTH
# =========================
def login_and_get_xauth():
    options = Options()
    options.add_argument("--start-maximized")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    wait = WebDriverWait(driver, 30)

    print("🔐 Login KipApp...")
    driver.get("https://kipapp.bps.go.id/#/auth/login")

    # Klik Login SSO
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[.//span[text()='Login SSO']]")
        )
    ).click()

    # Login SSO BPS
    wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(USERNAME)
    wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys(PASSWORD)
    driver.find_element(By.ID, "kc-login").click()

    wait.until(EC.url_contains("kipapp.bps.go.id"))
    time.sleep(3)

    # Trigger API agar X-Auth muncul
    driver.get("https://kipapp.bps.go.id/api/v1/user")
    time.sleep(2)

    token = None
    logs = driver.get_log("performance")

    for entry in logs:
        msg = json.loads(entry["message"])["message"]
        if msg["method"] == "Network.requestWillBeSent":
            headers = msg["params"]["request"].get("headers", {})
            if "X-Auth" in headers:
                token = headers["X-Auth"]
                break

    driver.quit()

    if not token:
        raise Exception("❌ X-Auth gagal diambil")

    print("✅ X-Auth berhasil")
    return token

# =========================
# AMBIL PEGAWAI & PERIODE
# =========================
def get_pegawai_dan_periode(x_auth):
    r = requests.get(
        f"{BASE_URL}/dashboard/skpbulanini",
        headers={
            "X-Auth": x_auth,
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        },
        params={"niplama": NIP_LAMA}
    )
    r.raise_for_status()
    data = r.json()

    pegawai_id = data["skp"]["raw"]["pegawaiid"]
    periode_id = data["skp"]["raw"]["periodeid"]
    tahun = data["skp"]["raw"]["tahun"]

    print(f"👤 Pegawai ID : {pegawai_id}")
    print(f"📆 Periode ID : {periode_id}")
    print(f"🗓️  Tahun     : {tahun}")

    return pegawai_id, periode_id, tahun

# =========================
# AMBIL DATA SKP
# =========================
def get_skp(x_auth, pegawai_id, periode_id):
    url = f"{BASE_URL}/skp"
    params = {
        "pegawaiid": pegawai_id,
        "periodeid": periode_id
    }

    r = requests.get(
        url,
        headers={
            "X-Auth": x_auth,
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        },
        params=params
    )
    r.raise_for_status()
    return r.json()

# =========================
# AMBIL RENCANA KINERJA
# =========================
def get_rencana_kinerja(x_auth, skp_id):
    url = f"{BASE_URL}/skp/rk"
    params = {
        "skpid": skp_id,
        "direct": 1
    }

    r = requests.get(
        url,
        headers={
            "X-Auth": x_auth,
            "Accept": "application/json",
            "User-Agent": "Mozilla/5.0"
        },
        params=params
    )
    r.raise_for_status()
    return r.json()

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    x_auth = login_and_get_xauth()
    pegawai_id, periode_id, tahun = get_pegawai_dan_periode(x_auth)

    skp_data = get_skp(x_auth, pegawai_id, periode_id)

    # ======================
    # SKP TAHUNAN (periodepenilaianid = None)
    # ======================
    skp_tahunan = [i for i in skp_data if i["periodepenilaianid"] is None]
    skp_id = skp_tahunan[0]["id"]

    print(f"📌 SKP Tahunan ID: {skp_id}")

    rk_data = get_rencana_kinerja(x_auth, skp_id)

    rows = []
    for i in rk_data:
        rows.append({
            "rkid": i.get("rkid"),
            "rencana_kinerja": i.get("rencanakinerja"),
            "rencana_kinerja_atasan": i.get("rencanakinerjaatasan"),
            "tahun": i.get("tahun"),
            "tim": i.get("namatim")
        })

    df = pd.DataFrame(rows)
    df.to_excel("Rencana_Kinerja_Tahunan.xlsx", index=False)

    print("✅ Rencana_Kinerja_Tahunan.xlsx berhasil dibuat")

    # ======================
    # SKP BULANAN (NONAKTIF)
    # ======================
    """
    skp_bulanan = [i for i in skp_data if i["periodepenilaianid"] is not None]
    for b in skp_bulanan:
        print(b["keteranganperiodepenilaian"], b["nilaiprestasi"])
    """
