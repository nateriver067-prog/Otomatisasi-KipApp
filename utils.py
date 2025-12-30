import time
import requests
from logger import logger


class UnauthorizedError(Exception):
    pass


def get_with_retry(
    url,
    headers,
    params=None,
    retries=3,
    delay=2,
    timeout=15
):
    for attempt in range(retries + 1):
        r = requests.get(url, headers=headers, params=params)

        if r.status_code == 401:
            logger.error(
                f"❌ 401 Unauthorized | URL={url} | params={params}"
            )
            raise UnauthorizedError()

        if r.status_code >= 400:
            logger.error(
                f"❌ HTTP {r.status_code} | URL={url} | response={r.text}"
            )
            r.raise_for_status()

        return r.json()

    raise Exception("❌ API gagal setelah retry")
