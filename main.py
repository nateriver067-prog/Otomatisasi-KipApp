from auth import login_and_get_xauth
from api import (
    get_dashboard_skp_bulan_ini,
    get_rencana_kinerja_bulanan,
    get_pelaksanaan_bulanan
)
from parser import (
    parse_rencana_kinerja_bulanan,
    parse_pelaksanaan
)
from logger import logger
from config import NIP_LAMA
from utils import UnauthorizedError
import pandas as pd


def main():
    logger.info("🚀 Program dimulai (MODE RK BULANAN FINAL)")

    # ======================
    # LOGIN
    # ======================
    x_auth = login_and_get_xauth()
    
# 2. ambil dashboard bulan aktif
    try:
        dashboard = get_dashboard_skp_bulan_ini(x_auth)
        skpid_bulan = dashboard["skp"]["raw"]["id"]
    except UnauthorizedError:
        logger.warning("🔄 Token expired, login ulang...")
        x_auth = login_and_get_xauth()
        dashboard = get_dashboard_skp_bulan_ini(x_auth)
        skpid_bulan = dashboard["skp"]["raw"]["id"]

    # ======================
    # AMBIL SKP BULAN AKTIF
    # ======================
    skp_raw = dashboard["skp"]["raw"]
    skpid_bulan = skp_raw["id"]
    periode_id = skp_raw["periodeid"]
    periode_penilaian_id = skp_raw["periodepenilaianid"]
    tahun = skp_raw["tahun"]

    logger.info(f"📌 SKP BULAN AKTIF ID : {skpid_bulan}")
    logger.info(f"📆 Periode ID        : {periode_id}")
    logger.info(f"🗓️  Tahun            : {tahun}")

    # ======================
    # Ambil RK BULANAN + IKI
    # ======================
    try:
        rk_data = get_rencana_kinerja_bulanan(x_auth, skpid_bulan)
    except UnauthorizedError:
        logger.warning("🔄 Token expired saat ambil RK, login ulang...")
        x_auth = login_and_get_xauth()
        rk_data = get_rencana_kinerja_bulanan(x_auth, skpid_bulan)

    # 4. parse ke dataframe
    df_rk = parse_rencana_kinerja_bulanan(rk_data)

    # ======================
    # PELAKSANAAN BULANAN
    # ======================
    try:
        pelaksanaan_data = get_pelaksanaan_bulanan(
            x_auth,
            periode_id,
            periode_penilaian_id,
            NIP_LAMA
        )
    except UnauthorizedError:
        logger.warning("🔄 Token expired saat ambil pelaksanaan, login ulang...")
        x_auth = login_and_get_xauth()
        pelaksanaan_data = get_pelaksanaan_bulanan(
            x_auth,
            periode_id,
            periode_penilaian_id,
            NIP_LAMA
        )

    df_pelaksanaan = parse_pelaksanaan(pelaksanaan_data)

    # ======================
    # EXPORT EXCEL (2 SHEET)
    # ======================
    output_file = "output/KipApp_Pelaksanaan_dan_RK.xlsx"

    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
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

        ws_pel = writer.sheets["Pelaksanaan"]
        ws_rk  = writer.sheets["Rencana_Kinerja_Bulanan"]

        last_row = len(df_pelaksanaan) + 1

        # ======================
        # DROPDOWN RK
        # ======================
        ws_pel.data_validation(
            f"C2:C{last_row}",
            {
                "validate": "list",
                "source": f"='Rencana_Kinerja_Bulanan'!$B$2:$B${len(df_rk)+1}",
                "input_title": "Pilih RK",
                "input_message": "Pilih rencana kinerja"
            }
        )

        # ======================
        # AUTO COPY RKID
        # ======================
        for row in range(2, last_row + 1):
            ws_pel.write_formula(
                f"D{row}",
                (
                    "=IFERROR("
                    "XLOOKUP("
                    f"C{row},"
                    "'Rencana_Kinerja_Bulanan'!$B:$B,"
                    "'Rencana_Kinerja_Bulanan'!$A:$A"
                    "),"
                    "\"\""
                    ")"
                )
            )


    logger.info(f"✅ File berhasil dibuat: {output_file}")


if __name__ == "__main__":
    main()
