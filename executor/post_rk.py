import json
import pandas as pd

from auth.kipapp import login_and_get_xauth
from api.skp import get_dashboard_skp_bulan_ini
from logger import logger
from utils import get_with_retry
from config import set_enable_post_rk_false, ENABLE_POST_RK,validate_env

EXCEL_FILE = "output/KipApp_Pelaksanaan_dan_RK.xlsx"
SHEET_NAME = "Rencana_Kinerja_Bulanan"


def main(dry_run=False):
    validate_env()
    logger.info("🚀 POST RK BULANAN")

    # ======================
    # SAFETY FLAG
    # ======================
    if not ENABLE_POST_RK:
        logger.warning("⏭️ POST RK dilewati (enable_post_rk = false)")
        return

    if dry_run:
        logger.warning("🧪 DRY RUN AKTIF — RK TIDAK AKAN DIPOST")

    # ======================
    # LOGIN & DASHBOARD
    # ======================
    x_auth = login_and_get_xauth()
    dashboard = get_dashboard_skp_bulan_ini(x_auth)

    skp_raw = dashboard["skp"]["raw"]

    payload = {
        "id": str(skp_raw["id"]),
        "periodepenilaianid": skp_raw["periodepenilaianid"],
        "data": [],
        "flagmethod": 2
    }

    # ======================
    # LOAD EXCEL
    # ======================
    df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)

    for _, row in df.iterrows():
        if not row.get("iki_ids"):
            continue

        payload["data"].append({
            "rk": str(row["rkid"]),
            "iki": str(row["iki_ids"]).split(","),
            "flagrk": 1
        })

    if not payload["data"]:
        logger.error("❌ Tidak ada RK valid untuk dipost")
        return

    logger.info(f"📦 Total RK siap diproses: {len(payload['data'])}")

    # ======================
    # DRY RUN EXIT
    # ======================
    if dry_run:
        logger.info("🧪 DRY RUN SELESAI — tidak ada data dikirim")
        logger.debug(json.dumps(payload, indent=2))
        return

    # ======================
    # POST KE SERVER
    # ======================
    logger.info("📤 Kirim RK ke server...")
    resp = get_with_retry(
        "https://kipapp.bps.go.id/api/v1/skp/bulanan",
        method="POST",
        headers={
            "X-Auth": x_auth,
            "Content-Type": "application/json"
        },
        json=payload
    )

    logger.info("✅ RK BULANAN BERHASIL DIAKTIFKAN")
    logger.debug(json.dumps(resp, indent=2))

    # ======================
    # LOCK RK (ONE TIME ONLY)
    # ======================
    set_enable_post_rk_false()
    logger.warning("🔒 enable_post_rk otomatis diset FALSE")


if __name__ == "__main__":
    main()
