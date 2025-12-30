import time
import json
import requests
import pandas as pd
from tqdm import tqdm

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

    print("🔐 Membuka halaman login KipApp...")
    driver.get("https://kipapp.bps.go.id/#/auth/login")

    # Klik tombol Login SSO
    login_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[.//span[text()='Login SSO']]")
        )
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", login_btn)
    time.sleep(0.5)
    login_btn.click()

    # Login SSO
    wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(USERNAME)
    wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys(PASSWORD)
    driver.find_element(By.ID, "kc-login").click()

    # Tunggu redirect balik ke KipApp
    wait.until(EC.url_contains("kipapp.bps.go.id"))
    time.sleep(3)

    # Trigger API agar token muncul
    driver.get("https://kipapp.bps.go.id/api/v1/user")
    time.sleep(2)

    print("🔎 Mengambil X-Auth dari network log...")
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
        raise Exception("❌ X-Auth tidak ditemukan, login gagal")

    print("✅ X-Auth berhasil didapatkan")
    return token

# =========================
# AMBIL PEGAWAI ID + PERIODE ID
# =========================
def get_pegawai_dan_periode(x_auth, niplama):
    url = f"{BASE_URL}/dashboard/skpbulanini"

    headers = {
        "X-Auth": x_auth,
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    params = {"niplama": niplama}

    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()

    data = r.json()

    pegawai_id = data["skp"]["raw"]["pegawaiid"]
    periode_id = data["tahun"]["value"]
    tahun = data["tahun"]["label"]

    print(f"✅ Pegawai ID  : {pegawai_id}")
    print(f"✅ Periode ID  : {periode_id} (Tahun {tahun})")

    return pegawai_id, periode_id, tahun

# =========================
# SCRAP DATA 1 TAHUN
# =========================
def scrap_1_tahun(x_auth, pegawai_id, periode_id, tahun):
    headers = {
        "X-Auth": x_auth,
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }

    print("📥 Mengambil daftar SKP bulanan...")
    skp_res = requests.get(
        f"{BASE_URL}/skp",
        headers=headers,
        params={
            "periodeid": periode_id,
            "pegawaiid": pegawai_id,
            "jenis": 2
        }
    )
    skp_res.raise_for_status()
    skp_list = skp_res.json()

    rows = []

    for skp in tqdm(skp_list, desc="📆 Proses per bulan"):
        skpid = skp["id"]
        bulan = skp["keteranganperiodepenilaian"]

        keg_res = requests.get(
            f"{BASE_URL}/kegiatan",
            headers=headers,
            params={"skpid": skpid}
        )

        if keg_res.status_code != 200:
            continue

        for k in keg_res.json():
            rows.append({
                "tahun": tahun,
                "bulan": bulan,
                "tanggal": k.get("tanggal"),
                "rencana_kinerja": k.get("rencanakinerja"),
                "kegiatan": k.get("kegiatan"),
                "capaian": k.get("capaian"),
                "progres": k.get("progres")
            })

    df = pd.DataFrame(rows)
    output = f"kipapp_kinerja_{tahun}.xlsx"
    df.to_excel(output, index=False)

    print(f"✅ Selesai! File tersimpan: {output}")

# =========================
# MAIN
# =========================
if __name__ == "__main__":
    x_auth = login_and_get_xauth()
    pegawai_id, periode_id, tahun = get_pegawai_dan_periode(x_auth, NIP_LAMA)
    scrap_1_tahun(x_auth, pegawai_id, periode_id, tahun)
