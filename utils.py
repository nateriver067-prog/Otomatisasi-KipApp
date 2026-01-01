import time
import random
import requests
from logger import logger


class UnauthorizedError(Exception):
    pass


class SkipError(Exception):
    pass


RETRYABLE_STATUS = {429, 500, 502, 503, 504}


def sleep_jitter(base=2.5, spread=4.0, label=""):
    duration = random.uniform(base, base + spread)
    if label:
        logger.debug(f"[DELAY] {label} sleep {duration:.2f}s")
    time.sleep(duration)


def request_with_retry(
    method,
    url,
    headers,
    params=None,
    json=None,
    data=None,
    retries=3,
    timeout=15,
    delay_base=2.5,
    delay_spread=4.0,
    label="",
):
    """
    HTTP request wrapper dengan:
    - retry selektif
    - jitter delay
    - aman untuk GET / POST
    """

    last_exc = None

    for attempt in range(1, retries + 1):
        try:
            r = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json,
                data=data,
                timeout=timeout,
            )

            if r.status_code == 401:
                logger.error(f"❌ 401 Unauthorized | {url}")
                raise UnauthorizedError()

            if r.status_code >= 400:
                if r.status_code in RETRYABLE_STATUS:
                    raise requests.HTTPError(
                        f"Retryable HTTP {r.status_code}", response=r
                    )
                else:
                    logger.error(
                        f"❌ HTTP {r.status_code} | {url} | {r.text}"
                    )
                    r.raise_for_status()

            try:
                return r.json()
            except ValueError:
                return r.text

        except UnauthorizedError:
            raise

        except Exception as e:
            last_exc = e
            logger.warning(
                f"⚠️ Attempt {attempt}/{retries} gagal [{label}]: {e}"
            )

            if attempt == retries:
                break

            sleep_jitter(
                base=delay_base,
                spread=delay_spread,
                label=f"{label} retry-{attempt}",
            )

    raise last_exc
