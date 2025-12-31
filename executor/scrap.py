# executor/scrap.py
import pandas as pd

from auth.kipapp import login_and_get_xauth
from api.skp import (
    get_dashboard_skp_bulan_ini,
    get_rencana_kinerja_bulanan,
    get_pelaksanaan_bulanan,
)
from parser.rk_parser import parse_rencana_kinerja_bulanan
from parser.pelaksanaan_parser import parse_pelaksanaan
from logger import logger
from config import OUTPUT_DIR,validate_env


OUTPUT_FILE = f"{OUTPUT_DIR}/KipApp_Pelaksanaan_dan_RK.xlsx"


def main():
    validate_env()
    logger.info("🚀 SCRAP DATA KIPAPP (RK + PELAKSANAAN)")

    # ======================
    # LOGIN
    # ======================
    x_auth = login_and_get_xauth()
    dashboard = get_dashboard_skp_bulan_ini(x_auth)

    skp_raw = dashboard["skp"]["raw"]
    skpid_bulan = skp_raw["id"]
    periode_id = skp_raw["periodeid"]
    periode_penilaian_id = skp_raw["periodepenilaianid"]
    niplama = dashboard["pegawai"]["raw"]["niplama"]

    logger.info(f"📌 SKP BULAN ID : {skpid_bulan}")

    # ======================
    # AMBIL RK BULANAN
    # ======================
    rk_data = get_rencana_kinerja_bulanan(x_auth, skpid_bulan)
    df_rk = parse_rencana_kinerja_bulanan(rk_data)

    # ======================
    # AMBIL PELAKSANAAN
    # ======================
    pelaksanaan_data = get_pelaksanaan_bulanan(
        x_auth,
        periode_id,
        periode_penilaian_id,
        niplama
    )
    df_pelaksanaan = parse_pelaksanaan(pelaksanaan_data)

    # ======================
    # EXPORT EXCEL
    # ======================
    with pd.ExcelWriter(OUTPUT_FILE, engine="xlsxwriter") as writer:
        df_pelaksanaan.to_excel(
            writer,
            sheet_name="Pelaksanaan",
            index=False
        )
        df_rk.to_excel(
            writer,
            sheet_name="Rencana_Kinerja_Bulanan",
            index=False
        )

    logger.info(f"✅ File berhasil dibuat: {OUTPUT_FILE}")
