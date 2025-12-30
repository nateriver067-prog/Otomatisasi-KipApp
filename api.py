from config import BASE_URL, USER_AGENT, NIP_LAMA
from utils import get_with_retry
from logger import logger


def get_pegawai_dan_periode(x_auth):
    logger.info("📥 Ambil pegawai & periode")
    return get_with_retry(
        f"{BASE_URL}/dashboard/skpbulanini",
        headers={
            "X-Auth": x_auth,
            "User-Agent": USER_AGENT
        },
        params={"niplama": NIP_LAMA}
    )


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


def get_rencana_kinerja(x_auth, skpid):
    logger.info(f"📥 Ambil RK (skpid={skpid})")

    return get_with_retry(
        f"{BASE_URL}/skp/rk",
        headers={"X-Auth": x_auth},
        params={"skpid": skpid, "direct": 1}
    )


def get_presensi(x_auth, periode_id, periode_penilaian_id, niplama):
    logger.info(
        f"📥 Ambil presensi (periode_penilaian_id={periode_penilaian_id})"
    )

    return get_with_retry(
        f"{BASE_URL}/kegiatan/presensi",
        headers={"X-Auth": x_auth},
        params={
            "periodeid": periode_id,
            "periodepenilaianid": periode_penilaian_id,
            "niplama": niplama
        }
    )

def get_pelaksanaan_bulanan(x_auth, periode_id, periode_penilaian_id, niplama):
    logger.info(
        f"➡️ API presensi | periode_id={periode_id}, "
        f"periode_penilaian_id={periode_penilaian_id}, niplama={niplama}"
    )

    data = get_with_retry(
        f"{BASE_URL}/kegiatan/presensi",
        headers={"X-Auth": x_auth},
        params={
            "periodeid": periode_id,
            "periodepenilaianid": periode_penilaian_id,
            "niplama": niplama
        }
    )

    logger.info(f"⬅️ Data pelaksanaan diterima: {len(data)} record")
    return data
