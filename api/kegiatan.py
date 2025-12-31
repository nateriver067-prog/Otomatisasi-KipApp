from config import BASE_URL, USER_AGENT
from utils import get_with_retry
from logger import logger


def get_existing_kegiatan(x_auth, skpid):
    logger.info("📥 Ambil kegiatan existing")

    data = get_with_retry(
        f"{BASE_URL}/kegiatan",
        headers={
            "X-Auth": x_auth,
            "User-Agent": USER_AGENT
        },
        params={"skpid": skpid}
    )

    return {(str(k["rkid"]), k["tanggal"]) for k in data}


def post_pelaksanaan(x_auth, skpid, rkid, tanggal, kegiatan, datadukung):
    payload = {
        "skpid": str(skpid),
        "rkid": str(rkid),
        "kegiatan": kegiatan,
        "tanggal": tanggal,
        "tanggalselesai": tanggal,
        "progres": 100,
        "capaian": f"Telah {kegiatan}",
        "datadukung": datadukung,
        "iscapaianskp": 0
    }

    r = get_with_retry(
        f"{BASE_URL}/kegiatan",
        method="POST",
        headers={
            "X-Auth": x_auth,
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT
        },
        json=payload
    )

    return r
