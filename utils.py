import time
import requests
from logger import logger


class UnauthorizedError(Exception):
    pass


class SkipError(Exception):
    pass


def get_with_retry(
    url,
    headers,
    params=None,
    method="GET",
    json=None,
    data=None,
    retries=3,
    delay=2,
    timeout=15,
):
    """
    HTTP wrapper dengan retry.
    Support:
    - GET / POST
    - params
    - json body
    - data body
    """

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
                logger.error(
                    f"❌ 401 Unauthorized | URL={url} | params={params}"
                )
                raise UnauthorizedError()

            if r.status_code >= 400:
                logger.error(
                    f"❌ HTTP {r.status_code} | URL={url} | response={r.text}"
                )
                r.raise_for_status()

            # default: JSON response
            try:
                return r.json()
            except ValueError:
                return r.text

        except UnauthorizedError:
            raise

        except Exception as e:
            logger.warning(
                f"⚠️ Attempt {attempt}/{retries} gagal: {e}"
            )
            if attempt == retries:
                raise
            time.sleep(delay)
