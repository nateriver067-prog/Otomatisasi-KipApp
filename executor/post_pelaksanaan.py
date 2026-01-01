import pandas as pd
from tqdm import tqdm

from auth.kipapp import login_and_get_xauth
from api.skp import (
    get_dashboard_skp_bulan_ini,
    get_pelaksanaan_bulanan,
    get_rk_dropdown_bulanan,   # ✅ endpoint BENAR
)
from logger import logger
from config import (
    EXCEL_PELAKSANAAN,
    SHEET_PELAKSANAAN,
    EXCEL_LINKS,
    validate_env,
    NIP_LAMA,
)
from utils import request_with_retry,sleep_jitter   

BASE_URL = "https://kipapp.bps.go.id/api/v1"


# ==================================================
# POST 1 PELAKSANAAN
# ==================================================
def post_pelaksanaan(
    x_auth,
    skpid_bulan,
    rkid,
    tanggal,
    kegiatan,
    datadukung,
    safe_cfg,
):
    payload = {
        "skpid": str(skpid_bulan),
        "rkid": str(rkid),
        "kegiatan": kegiatan,
        "tanggal": tanggal,
        "tanggalselesai": tanggal,
        "progres": 100,
        "capaian": f"Telah {kegiatan}",
        "datadukung": datadukung,
        "iscapaianskp": 0,
    }

    return request_with_retry(
        method="POST",
        url=f"{BASE_URL}/kegiatan",
        headers={
            "X-Auth": x_auth,
            "Content-Type": "application/json",
        },
        json=payload,
        retries=safe_cfg["retries"],
        delay_base=safe_cfg["delay_base"],
        delay_spread=safe_cfg["delay_spread"],
        label=f"{tanggal}",
    )

# ==================================================
# MAIN
# ==================================================
def main(dry_run=False, safe_cfg=None):
    if safe_cfg is None:
        safe_cfg = {
        "retries": 1,
        "delay_base": 1.5,
        "delay_spread": 2.0,
        "circuit_breaker": None,
    }
    logger.info(
    f"⚙️ Runtime config | retries={safe_cfg['retries']} "
    f"| delay={safe_cfg['delay_base']}–"
    f"{safe_cfg['delay_base'] + safe_cfg['delay_spread']}s "
    f"| circuit_breaker={safe_cfg['circuit_breaker']}"
    )   

    validate_env()
    logger.info("🚀 POST PELAKSANAAN BULANAN")

    if dry_run:
        logger.warning("🧪 DRY RUN AKTIF — TIDAK ADA POST")

    # ======================
    # LOGIN & DASHBOARD
    # ======================
    x_auth = login_and_get_xauth()
    dashboard = get_dashboard_skp_bulan_ini(x_auth)

    skp_raw = dashboard["skp"]["raw"]
    skpid_bulan = skp_raw["id"]
    periode_id = skp_raw["periodeid"]
    periode_penilaian_id = skp_raw["periodepenilaianid"]

    logger.info(f"📌 SKP BULAN ID : {skpid_bulan}")

    # ======================
    # RK BULANAN (DROPDOWN)
    # ======================
    rk_list = get_rk_dropdown_bulanan(x_auth, skpid_bulan)

    rk_map = {
        rk["rencanakinerja"].strip().lower(): str(rk["rkid"])
        for rk in rk_list
        if rk.get("rkid") and rk.get("rencanakinerja")
    }

    logger.info(f"📋 RK bulanan aktif (dropdown): {len(rk_map)}")

    if not rk_map:
        logger.error("❌ RK bulanan kosong — pelaksanaan tidak bisa dipost")
        return

    # ======================
    # PELAKSANAAN EXISTING
    # ======================
    existing_data = get_pelaksanaan_bulanan(
        x_auth,
        periode_id,
        periode_penilaian_id,
        NIP_LAMA,
    )

    existing_keys = {
        (str(i.get("rkid")), i.get("tanggal"))
        for i in existing_data
        if i.get("rkid") and i.get("tanggal")
    }

    # ======================
    # LOAD DRIVE LINKS
    # ======================
    df_links = pd.read_excel(EXCEL_LINKS)
    link_map = dict(
        zip(
            df_links["tanggal"].astype(str),
            df_links["share_link"].astype(str),
        )
    )

    # ======================
    # LOAD EXCEL PELAKSANAAN
    # ======================
    df = pd.read_excel(EXCEL_PELAKSANAAN, sheet_name=SHEET_PELAKSANAAN)

    sukses = skip = gagal = 0

    # ======================
    # LOOP UTAMA
    # ======================
    error_streak = 0
    MAX_ERROR_STREAK = safe_cfg["circuit_breaker"]

    for _, row in tqdm(df.iterrows(), total=len(df), desc="📤 Post Pelaksanaan"):
        ...
        if dry_run:
            logger.info(f"[DRY RUN] {tanggal} | {kegiatan}")
            sukses += 1
            continue

        try:
            post_pelaksanaan(
                x_auth,
                skpid_bulan,
                rkid,
                tanggal,
                kegiatan,
                link_map[tanggal],
                safe_cfg,
            )
            sukses += 1
            error_streak = 0

            sleep_jitter(
                safe_cfg["delay_base"],
                safe_cfg["delay_spread"],
                label="after pelaksanaan",
            )

        except Exception as e:
            gagal += 1
            error_streak += 1
            logger.exception(f"❌ Gagal post {tanggal}: {e}")

            if MAX_ERROR_STREAK and error_streak >= MAX_ERROR_STREAK:
                logger.critical(
                    "🛑 Terlalu banyak error berturut-turut. Proses dihentikan demi keamanan."
                )
                break

    # ======================
    # SUMMARY
    # ======================
    logger.info("=== SELESAI POST PELAKSANAAN ===")
    logger.info(f"✅ Berhasil : {sukses}")
    logger.info(f"⏭️ Skip     : {skip}")
    logger.info(f"❌ Gagal    : {gagal}")
