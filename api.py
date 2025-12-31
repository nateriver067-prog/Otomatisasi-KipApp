from config import BASE_URL, USER_AGENT, NIP_LAMA
from utils import get_with_retry
from logger import logger


# =========================
# DASHBOARD (SUMBER KEBENARAN)
# =========================
def get_dashboard_skp_bulan_ini(x_auth):
    logger.info("📥 Ambil dashboard SKP bulan aktif")

    return get_with_retry(
        f"{BASE_URL}/dashboard/skpbulanini",
        headers={
            "X-Auth": x_auth,
            "User-Agent": USER_AGENT
        },
        params={"niplama": NIP_LAMA}
    )


# =========================
# RENCANA KINERJA BULANAN (FINAL)
# =========================
def get_rencana_kinerja_bulanan(x_auth, skpid_bulan):
    """
    RK yang dipakai untuk:
    - pelaksanaan
    - centang RK bulanan
    - POST /skp/bulanan
    """
    logger.info(f"📥 Ambil RK bulanan + IKI | skpid={skpid_bulan}")

    data = get_with_retry(
        f"{BASE_URL}/skp/rk/copy/bulanan",
        headers={
            "X-Auth": x_auth,
            "User-Agent": USER_AGENT
        },
        params={"skpid": skpid_bulan}
    )

    rk_list = data.get("rk", [])
    logger.info(f"⬅️ RK bulanan diterima: {len(rk_list)} item")

    return rk_list

# =========================
# PELAKSANAAN BULANAN
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
