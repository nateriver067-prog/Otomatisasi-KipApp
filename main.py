from auth import login_and_get_xauth
from api import (
    get_pegawai_dan_periode,
    get_skp_list,
    get_rencana_kinerja_bulanan,
    get_pelaksanaan_bulanan
)
from parser import (
    parse_rencana_kinerja,
    parse_pelaksanaan
)
from logger import logger
from config import NIP_LAMA, ONLY_LAST_MONTH
from utils import UnauthorizedError
import pandas as pd


def main():
    # ======================
    # MENU (DISIAPKAN UNTUK FUTURE)
    # ======================
    print("\n=== MENU KIPAPP ===")
    print("1. Ambil Rencana Kinerja Tahunan")
    print("2. Ambil Pelaksanaan Bulanan")
    print("3. Ambil RK Tahunan + Pelaksanaan (DEFAULT)")
    print("0. Keluar")

    pilihan = input("Pilih menu (0-3): ").strip()

    if pilihan == "0":
        print("👋 Keluar program")
        return

    if pilihan not in ("1", "2", "3"):
        print("❌ Pilihan tidak valid")
        return

    # =====================================
    # SEMUA PILIHAN → MODE GABUNG (3)
    # =====================================
    logger.info("🚀 Program dimulai (MODE GABUNG)")

    # ======================
    # LOGIN
    # ======================
    x_auth = login_and_get_xauth()

    try:
        meta = get_pegawai_dan_periode(x_auth)
    except UnauthorizedError:
        logger.warning("🔄 Token expired, login ulang...")
        x_auth = login_and_get_xauth()
        meta = get_pegawai_dan_periode(x_auth)

    pegawai_id = meta["skp"]["raw"]["pegawaiid"]
    periode_id = meta["skp"]["raw"]["periodeid"]

    logger.info(f"👤 Pegawai ID : {pegawai_id}")
    logger.info(f"📆 Periode ID : {periode_id}")

    # ======================
    # AMBIL SKP
    # ======================
    try:
        skp_list = get_skp_list(x_auth, pegawai_id, periode_id)
    except UnauthorizedError:
        logger.warning("🔄 Token expired saat ambil SKP, login ulang...")
        x_auth = login_and_get_xauth()
        skp_list = get_skp_list(x_auth, pegawai_id, periode_id)

    # ======================
    # RK TAHUNAN
    # ======================
    skp_tahunan = [i for i in skp_list if i["periodepenilaianid"] is None]

    if not skp_tahunan:
        logger.critical("❌ SKP tahunan tidak ditemukan")
        return

    skp_id = skp_tahunan[0]["id"]
    logger.info(f"📌 SKP Tahunan ID: {skp_id}")

    try:
        rk_data = get_rencana_kinerja_bulanan(x_auth, skp_id)
    except UnauthorizedError:
        logger.warning("🔄 Token expired saat ambil RK, login ulang...")
        x_auth = login_and_get_xauth()
        rk_data = get_rencana_kinerja_bulanan(x_auth, skp_id)

    df_rk = parse_rencana_kinerja(rk_data)

    # ======================
    # PELAKSANAAN BULANAN
    # ======================
    pelaksanaan_all = []

    skp_bulanan = [i for i in skp_list if i["periodepenilaianid"] is not None]

    if ONLY_LAST_MONTH and skp_bulanan:
        logger.info("🎯 Mode aktif: hanya ambil pelaksanaan bulan terakhir")
        skp_bulanan = [skp_bulanan[-1]]

    if not skp_bulanan:
        logger.warning("⚠️ Tidak ada SKP bulanan")
    else:
        for skp in skp_bulanan:
            bulan = skp["keteranganperiodepenilaian"]
            logger.info(f"📆 Ambil pelaksanaan bulan: {bulan}")

            try:
                data = get_pelaksanaan_bulanan(
                    x_auth,
                    periode_id,
                    skp["periodepenilaianid"],
                    NIP_LAMA
                )
            except UnauthorizedError:
                logger.warning("🔄 Token expired, login ulang...")
                x_auth = login_and_get_xauth()
                data = get_pelaksanaan_bulanan(
                    x_auth,
                    periode_id,
                    skp["periodepenilaianid"],
                    NIP_LAMA
                )

            pelaksanaan_all.extend(data)

    df_pelaksanaan = parse_pelaksanaan(pelaksanaan_all)

    # ======================
    # EXPORT EXCEL (2 SHEET)
    # ======================
    output_file = "output/KipApp_Pelaksanaan_dan_RK.xlsx"

    with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
        # Sheet Pelaksanaan
        df_pelaksanaan.to_excel(
            writer,
            sheet_name="Pelaksanaan",
            index=False
        )

        # Sheet RK
        df_rk.to_excel(
            writer,
            sheet_name="Rencana_Kinerja_Tahunan",
            index=False
        )

        workbook  = writer.book
        ws_pel = writer.sheets["Pelaksanaan"]
        ws_rk  = writer.sheets["Rencana_Kinerja_Tahunan"]

        # ======================
        # DROPDOWN RENCANA KINERJA
        # ======================
        last_row = len(df_pelaksanaan) + 1

        ws_pel.data_validation(
            f"C2:C{last_row}",
            {
                "validate": "list",
                "source": f"='Rencana_Kinerja_Tahunan'!$B$2:$B${len(df_rk)+1}",
                "input_title": "Pilih RK",
                "input_message": "Pilih rencana kinerja dari daftar"
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
                    "'Rencana_Kinerja_Tahunan'!$B:$B,"
                    "'Rencana_Kinerja_Tahunan'!$A:$A"
                    "),"
                    "\"\""
                    ")"
                )
            )


    logger.info(f"✅ File berhasil dibuat: {output_file}")


if __name__ == "__main__":
    main()
