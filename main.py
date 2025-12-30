from auth import login_and_get_xauth
from api import (
    get_pegawai_dan_periode,
    get_skp_list,
    get_rencana_kinerja,
    get_pelaksanaan_bulanan
)
from parser import (
    parse_rencana_kinerja,
    parse_pelaksanaan
)
from logger import logger
from config import NIP_LAMA
from utils import UnauthorizedError


def main():
    logger.info("🚀 Program dimulai")

    x_auth = login_and_get_xauth()

    try:
        meta = get_pegawai_dan_periode(x_auth)

    except UnauthorizedError:
        logger.warning("🔄 Token expired, login ulang...")
        x_auth = login_and_get_xauth()
        meta = get_pegawai_dan_periode(x_auth)

    pegawai_id = meta["skp"]["raw"]["pegawaiid"]
    periode_id = meta["skp"]["raw"]["periodeid"]

    try:
        skp_list = get_skp_list(x_auth, pegawai_id, periode_id)

    except UnauthorizedError:
        logger.warning("🔄 Token expired saat ambil SKP, login ulang...")
        x_auth = login_and_get_xauth()
        skp_list = get_skp_list(x_auth, pegawai_id, periode_id)

    skp_tahunan = [i for i in skp_list if i["periodepenilaianid"] is None]

    if not skp_tahunan:
        logger.critical("❌ SKP tahunan tidak ditemukan")
        return

    skp_id = skp_tahunan[0]["id"]
    logger.info(f"📌 SKP Tahunan ID: {skp_id}")

    try:
        rk_data = get_rencana_kinerja(x_auth, skp_id)

    except UnauthorizedError:
        logger.warning("🔄 Token expired saat ambil RK, login ulang...")
        x_auth = login_and_get_xauth()
        rk_data = get_rencana_kinerja(x_auth, skp_id)

    df = parse_rencana_kinerja(rk_data)
    df.to_excel("output/Rencana_Kinerja_Tahunan.xlsx", index=False)

    logger.info("✅ Export RK selesai")

    # ======================
    # PELAKSANAAN BULANAN
    # ======================
    pelaksanaan_all = []
    skp_bulanan = [i for i in skp_list if i["periodepenilaianid"] is not None]
    if ONLY_LAST_MONTH:
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
    df_pelaksanaan.to_excel(
        "output/Pelaksanaan_Bulanan.xlsx",
        index=False
    )
    
    logger.info("✅ Pelaksanaan_Bulanan.xlsx berhasil dibuat")



if __name__ == "__main__":
    main()
