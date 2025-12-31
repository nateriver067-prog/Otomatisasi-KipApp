# executor/scrap.py
import pandas as pd

from auth.kipapp import login_and_get_xauth
from api.skp import (
    get_dashboard_skp_bulan_ini,
    get_rencana_kinerja_tahunan,
    get_pelaksanaan_bulanan,
)
from parser.rk_parser import parse_rencana_kinerja_tahunan
from parser.pelaksanaan_parser import parse_pelaksanaan
from logger import logger
from config import OUTPUT_DIR, validate_env, NIP_LAMA


OUTPUT_FILE = f"{OUTPUT_DIR}/KipApp_Pelaksanaan_dan_RK.xlsx"


def main():
    # ======================
    # VALIDASI ENV
    # ======================
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

    logger.info(f"📌 SKP BULAN ID : {skpid_bulan}")
    logger.info(f"👤 NIP         : {NIP_LAMA}")

    # ======================
    # AMBIL RK Tahunan
    # ======================
    rk_data = get_rencana_kinerja_tahunan(x_auth, skpid_bulan)
    df_rk = parse_rencana_kinerja_tahunan(rk_data)

    # ======================
    # AMBIL PELAKSANAAN
    # ======================
    pelaksanaan_data = get_pelaksanaan_bulanan(
        x_auth,
        periode_id,
        periode_penilaian_id,
        NIP_LAMA
    )
    df_pelaksanaan = parse_pelaksanaan(pelaksanaan_data)

    # ======================
    # EXPORT EXCEL
    # ======================
    with pd.ExcelWriter(OUTPUT_FILE, engine="xlsxwriter") as writer:
        # ======================
        # TULIS DATA
        # ======================
        df_pelaksanaan.to_excel(
            writer,
            sheet_name="Pelaksanaan",
            index=False
        )

        df_rk.to_excel(
            writer,
            sheet_name="Rencana_Kinerja_Tahunan",
            index=False
        )

        wb = writer.book
        ws_pel = writer.sheets["Pelaksanaan"]
        ws_rk  = writer.sheets["Rencana_Kinerja_Tahunan"]

        last_row = len(df_pelaksanaan) + 1
        last_rk  = len(df_rk) + 1

        # ======================
        # 1️⃣ DROPDOWN RENCANA KINERJA
        # Kolom C (rencana_kinerja)
        # ======================
        ws_pel.data_validation(
            f"C2:C{last_row}",
            {
                "validate": "list",
                "source": f"='Rencana_Kinerja_Tahunan'!$B$2:$B${last_rk}",
                "input_title": "Pilih Rencana Kinerja",
                "input_message": "Ketik atau pilih rencana kinerja",
            }
        )

        # ======================
        # 2️⃣ AUTO ISI RKID (XLOOKUP)
        # Kolom D (rkid)
        # ======================
        for row in range(2, last_row + 1):
            ws_pel.write_formula(
                f"D{row}",
                (
                    "=IFERROR("
                    "XLOOKUP("
                    f"C{row},"
                    "'Rencana_Kinerja_Tahunan'!$B:$B,"
                    "'Rencana_Kinerja_Tahunan'!$A:$A"
                    "),"
                    "\"\""
                    ")"
                )
            )

