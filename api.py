from config import BASE_URL, USER_AGENT, NIP_LAMA
from utils import get_with_retry
from logger import logger


# =========================
# PEGAWAI & PERIODE
# =========================
def get_pegawai_dan_periode(x_auth):
    logger.info("📥 Ambil pegawai & periode aktif")

    return get_with_retry(
        f"{BASE_URL}/dashboard/skpbulanini",
        headers={
            "X-Auth": x_auth,
            "User-Agent": USER_AGENT
        },
        params={"niplama": NIP_LAMA}
    )


# =========================
# DAFTAR SKP
# =========================
def get_skp_list(x_auth, pegawai_id, periode_id):
    logger.info("📥 Ambil daftar SKP")

    return get_with_retry(
        f"{BASE_URL}/skp",
        headers={"X-Auth": x_auth},
        params={
            "pegawaiid": pegawai_id,
            "periodeid": periode_id
        }
    )


# =========================
# RENCANA KINERJA (BULANAN / FINAL)
# =========================
def get_rencana_kinerja_bulanan(x_auth, skpid):
    """
    RK yang BENAR untuk pelaksanaan:
    - RK awal tahun
    - RK tambahan
    - Status iscopied & isused
    """
    logger.info(f"📥 Ambil RK bulanan (copy) | skpid={skpid}")

    data = get_with_retry(
        f"{BASE_URL}/skp/rk/copy/bulanan",
        headers={
            "X-Auth": x_auth,
            "User-Agent": USER_AGENT
        },
        params={"skpid": skpid}
    )

    rk_list = data.get("rk", [])
    logger.info(f"⬅️ RK diterima: {len(rk_list)} item")

    return rk_list


# =========================
# PELAKSANAAN / PRESENSI
# =========================
def get_pelaksanaan_bulanan(x_auth, periode_id, periode_penilaian_id, niplama):
    logger.info(
        f"➡️ API presensi | "
        f"periode_id={periode_id}, "
        f"periode_penilaian_id={periode_penilaian_id}, "
        f"niplama={niplama}"
    )

    data = get_with_retry(
        f"{BASE_URL}/kegiatan/presensi",
        headers={
            "X-Auth": x_auth,
            "User-Agent": USER_AGENT
        },
        params={
            "periodeid": periode_id,
            "periodepenilaianid": periode_penilaian_id,
            "niplama": niplama
        }
    )

    logger.info(f"⬅️ Data pelaksanaan diterima: {len(data)} record")
    return data
