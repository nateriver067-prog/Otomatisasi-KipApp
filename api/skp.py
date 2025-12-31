from config import BASE_URL, USER_AGENT, NIP_LAMA
from utils import get_with_retry, UnauthorizedError
from logger import logger


# =========================
# DASHBOARD (SUMBER KEBENARAN)
# =========================
def get_dashboard_skp_bulan_ini(x_auth):
    """
    Sumber utama:
    - skpid bulan aktif
    - periodeid
    - periodepenilaianid
    """
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
# RENCANA KINERJA BULANAN (+ IKI)
# =========================
def get_rencana_kinerja_bulanan(x_auth, skpid_bulan):
    """
    RK BULANAN FINAL
    Dipakai untuk:
    - dropdown RK
    - mapping text RK → rkid
    - POST /skp/bulanan
    - POST pelaksanaan
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
# PELAKSANAAN (PRESENSI)
# =========================
def get_pelaksanaan_bulanan(x_auth, periode_id, periode_penilaian_id, niplama=None):
    """
    Presensi → bahan awal pelaksanaan
    """
    if not niplama:
        niplama = NIP_LAMA

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


# =========================
# POST KEGIATAN (PELENGKAP)
# =========================
def post_kegiatan(x_auth, payload):
    """
    POST /kegiatan
    Dipakai oleh post_pelaksanaan_full.py
    """
    logger.info(
        f"📤 POST kegiatan | "
        f"rkid={payload.get('rkid')} "
        f"tanggal={payload.get('tanggal')}"
    )

    return get_with_retry(
        f"{BASE_URL}/kegiatan",
        method="POST",
        headers={
            "X-Auth": x_auth,
            "User-Agent": USER_AGENT,
            "Content-Type": "application/json"
        },
        json=payload
    )
