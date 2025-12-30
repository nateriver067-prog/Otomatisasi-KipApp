import pandas as pd
import requests
from logger import logger

API_URL = "https://kipapp.bps.go.id/api/v1/skp/bulanan"

def entri_rk_bulanan_dari_excel(x_auth, excel_path):
    df = pd.read_excel(excel_path)

    headers = {
        "X-Auth": x_auth,
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://kipapp.bps.go.id/"
    }

    grouped = {}

    for _, row in df.iterrows():
        key = (str(row["skp_bulanan_id"]), int(row["periodepenilaianid"]))

        if key not in grouped:
            grouped[key] = []

        grouped[key].append({
            "rk": str(row["rkid"]),
            "iki": [],      # sengaja kosong
            "flagrk": 1
        })

    for (skp_bulanan_id, periodepenilaianid), rk_list in grouped.items():
        payload = {
            "id": skp_bulanan_id,
            "periodepenilaianid": periodepenilaianid,
            "data": rk_list,
            "flagmethod": 2
        }

        logger.info(
            f"🚀 Entri RK | SKP Bulanan={skp_bulanan_id} | BulanID={periodepenilaianid}"
        )

        r = requests.post(API_URL, headers=headers, json=payload)

        if r.status_code != 200:
            logger.error(f"❌ Gagal entri RK: {r.text}")
        else:
            logger.info("✅ RK berhasil diaktifkan")
