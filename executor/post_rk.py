# executor/post_rk.py
import json
import pandas as pd

from auth.kipapp import login_and_get_xauth
from api.skp import get_dashboard_skp_bulan_ini
from logger import logger
from config import (
    BASE_URL,
    EXCEL_PELAKSANAAN,
    ENABLE_POST_RK,
    set_enable_post_rk_false,
    validate_env,
)
from utils import request_with_retry


def main(dry_run: bool = False):
    validate_env()
    logger.info("🚀 POST RK BULANAN (WITH IKI)")

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
    skpid_bulan = str(skp_raw["id"])
    periode_penilaian_id = skp_raw["periodepenilaianid"]

    # ======================
    # LOAD EXCEL
    # ======================
    df_pel = pd.read_excel(
        EXCEL_PELAKSANAAN,
        sheet_name="Pelaksanaan"
    )

    df_rk = pd.read_excel(
        EXCEL_PELAKSANAAN,
        sheet_name="Rencana_Kinerja_Tahunan"
    )

    # ======================
    # BUILD RK → IKI MAP
    # ======================
    rk_iki_map = {}

    for _, row in df_rk.iterrows():
        rkid = str(row.get("rkid", "")).strip()
        iki_ids = str(row.get("iki_ids", "")).strip()

        if not rkid.isdigit():
            continue
        if not iki_ids or iki_ids.lower() == "nan":
            continue

        rk_iki_map[rkid] = [
            i.strip() for i in iki_ids.split(",") if i.strip().isdigit()
        ]

    if not rk_iki_map:
        logger.error("❌ Mapping RK → IKI kosong")
        return

    # ======================
    # AMBIL RKID DARI PELAKSANAAN (UNIK)
    # ======================
    used_rk = set()

    for _, row in df_pel.iterrows():
        rkid = str(row.get("rkid", "")).strip()

        if not rkid or not rkid.isdigit():
            continue

        used_rk.add(rkid)

    if not used_rk:
        logger.error("❌ Tidak ada RKID valid di sheet Pelaksanaan")
        return

    # ======================
    # BUILD PAYLOAD DATA
    # ======================
    data_payload = []

    for rkid in sorted(used_rk):
        iki = rk_iki_map.get(rkid)

        if not iki:
            logger.warning(f"⚠️ RK {rkid} tidak punya IKI → dilewati")
            continue

        data_payload.append({
            "rk": rkid,
            "iki": iki,
            "flagrk": 1
        })

    if not data_payload:
        logger.error("❌ Tidak ada RK + IKI valid untuk dipost")
        return

    logger.info(f"📦 Total RK akan dipost: {len(data_payload)}")

    payload = {
        "id": skpid_bulan,
        "periodepenilaianid": periode_penilaian_id,
        "data": data_payload,
        "flagmethod": 2
    }

    # ======================
    # DRY RUN
    # ======================
    if dry_run:
        logger.info("🧪 DRY RUN SELESAI — payload TIDAK dikirim")
        logger.debug(json.dumps(payload, indent=2))
        return

    # ======================
    # POST KE SERVER
    # ======================
    logger.info("📤 Mengirim RK ke server...")
    resp = request_with_retry(
        method="POST",
        url=f"{BASE_URL}/skp/bulanan",
        headers={
            "X-Auth": x_auth,
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Referer": "https://kipapp.bps.go.id/",
        },
        json=payload,
        retries=3,
        timeout=30,
        label="post-rk",
    )

    if isinstance(resp, dict) and resp.get("status") is False:
        raise RuntimeError(f"❌ Server menolak: {resp}")

    logger.info("✅ RK BULANAN BERHASIL DIAKTIFKAN")

    # ======================
    # ONE-TIME LOCK
    # ======================
    set_enable_post_rk_false()
    logger.warning("🔒 enable_post_rk diset FALSE (one-time)")


if __name__ == "__main__":
    main()
