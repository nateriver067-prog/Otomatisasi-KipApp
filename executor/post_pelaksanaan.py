import time
import pandas as pd
from tqdm import tqdm
import requests

from auth.auth import login_and_get_xauth
from api.skp import (
    get_dashboard_skp_bulan_ini,
    get_rencana_kinerja_bulanan,
    get_pelaksanaan_bulanan,
)
from logger import logger
from utils import UnauthorizedError
from config import (
    EXCEL_PELAKSANAAN,
    SHEET_PELAKSANAAN,
    EXCEL_LINKS,
    DELAY_POST,
)

BASE_URL = "https://kipapp.bps.go.id/api/v1"


# ======================
# POST 1 PELAKSANAAN
# ======================
def post_pelaksanaan(
    x_auth,
    skpid_bulan,
    rkid,
    tanggal,
    kegiatan,
    datadukung,
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

    r = requests.post(
        f"{BASE_URL}/kegiatan",
        headers={
            "X-Auth": x_auth,
            "Content-Type": "application/json",
        },
        json=payload,
    )

    if r.status_code != 200:
        raise RuntimeError(r.text)


# ======================
# MAIN
# ======================
def main(dry_run=False):
    logger.info("🚀 POST PELAKSANAAN FULL RUN")

    if dry_run:
        logger.warning("🧪 DRY RUN AKTIF — TIDAK ADA POST")

    # ======================
    # LOGIN
    # ======================
    x_auth = login_and_get_xauth()

    try:
        dashboard = get_dashboard_skp_bulan_ini(x_auth)
    except UnauthorizedError:
        logger.warning("🔄 Token expired, login ulang...")
        x_auth = login_and_get_xauth()
        dashboard = get_dashboard_skp_bulan_ini(x_auth)

    skp_raw = dashboard["skp"]["raw"]
    skpid_bulan = skp_raw["id"]
    periode_id = skp_raw["periodeid"]
    periode_penilaian_id = skp_raw["periodepenilaianid"]

    logger.info(f"📌 SKP BULAN ID : {skpid_bulan}")

    # ======================
    # RK BULANAN (SOURCE OF TRUTH)
    # ======================
    rk_list = get_rencana_kinerja_bulanan(x_auth, skpid_bulan)

    rk_map = {
        rk["rencanakinerja"].strip().lower(): str(rk["id"])
        for rk in rk_list
    }

    logger.info(f"📋 RK bulanan aktif: {len(rk_map)}")

    # ======================
    # PELAKSANAAN EXISTING
    # ======================
    existing_data = get_pelaksanaan_bulanan(
        x_auth,
        periode_id,
        periode_penilaian_id,
        dashboard["pegawai"]["raw"]["niplama"],
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
    for _, row in tqdm(df.iterrows(), total=len(df), desc="📤 Post Pelaksanaan"):
        tanggal = str(row["tanggal"]).strip()
        kegiatan = str(row["deskripsi"]).strip()
        teks_rk = str(row["rencana_kinerja"]).strip().lower()
        rkid = str(row["rkid"]).strip()

        # ===== VALIDASI =====
        if not tanggal or not kegiatan or not teks_rk:
            gagal += 1
            continue

        if not rkid.isdigit():
            logger.error(f"❌ RKID tidak valid: {rkid} ({tanggal})")
            gagal += 1
            continue

        if teks_rk not in rk_map:
            logger.error(f"❌ RK tidak ditemukan: {teks_rk}")
            gagal += 1
            continue

        if tanggal not in link_map:
            logger.error(f"❌ Link Drive tidak ditemukan: {tanggal}")
            gagal += 1
            continue

        key = (rkid, tanggal)
        if key in existing_keys:
            skip += 1
            continue

        # ===== DRY RUN =====
        if dry_run:
            logger.info(f"[DRY RUN] {tanggal} | {kegiatan}")
            sukses += 1
            continue

        # ===== POST =====
        try:
            post_pelaksanaan(
                x_auth,
                skpid_bulan,
                rkid,
                tanggal,
                kegiatan,
                link_map[tanggal],
            )
            sukses += 1
            time.sleep(DELAY_POST)

        except Exception as e:
            logger.exception(f"❌ Gagal post {tanggal}: {e}")
            gagal += 1

    # ======================
    # SUMMARY
    # ======================
    logger.info("=== SELESAI POST PELAKSANAAN ===")
    logger.info(f"✅ Berhasil : {sukses}")
    logger.info(f"⏭️ Skip     : {skip}")
    logger.info(f"❌ Gagal    : {gagal}")


if __name__ == "__main__":
    main()
