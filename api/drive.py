import time
import requests
import xml.etree.ElementTree as ET

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from config import USERNAME, PASSWORD
from logger import logger
from utils import UnauthorizedError

BASE_DAV = "https://drive.bps.go.id/remote.php/dav/files"
BASE_OCS = "https://drive.bps.go.id/ocs/v2.php/apps/files_sharing/api/v1/shares"


# ==================================================
# LOGIN DRIVE BPS (SSO) → COOKIE + REQUESTTOKEN
# ==================================================
def login_drive_session():
    logger.info("🔐 Login Drive BPS via SSO")

    options = Options()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    wait = WebDriverWait(driver, 30)
    driver.get("https://drive.bps.go.id")

    # klik SSO
    sso_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(text(), 'Single Sign-On BPS')]")
        )
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", sso_btn)
    time.sleep(0.5)
    sso_btn.click()

    # login keycloak
    wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(USERNAME)
    wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys(PASSWORD)
    driver.find_element(By.ID, "kc-login").click()

    wait.until(EC.url_contains("drive.bps.go.id"))
    time.sleep(3)

    cookies = {c["name"]: c["value"] for c in driver.get_cookies()}

    requesttoken = driver.execute_script(
        "return window.oc_requesttoken || (window.OC && OC.requestToken);"
    )

    driver.quit()

    if not requesttoken:
        raise UnauthorizedError("❌ requesttoken Drive tidak ditemukan")

    logger.info("✅ Session Drive siap")
    return cookies, requesttoken


# ==================================================
# AUTO DETECT USER_ID (DAV)
# ==================================================
def get_drive_user_id(cookies, requesttoken=None):
    """
    Ambil USER_ID Drive dari cookie nc_username
    (paling stabil di Drive BPS)
    """
    user_id = cookies.get("nc_username")

    if not user_id:
        raise Exception("❌ USER_ID Drive tidak ditemukan di cookie nc_username")

    return user_id


# ==================================================
# MKCOL (SAFE)
# ==================================================
def create_folder(user_id, path, cookies, requesttoken):
    """
    Membuat folder (aman dijalankan berulang)
    """
    url = f"{BASE_DAV}/{user_id}/{path}".replace(" ", "%20")

    r = requests.request(
        "MKCOL",
        url,
        headers={"requesttoken": requesttoken},
        cookies=cookies
    )

    if r.status_code in (201, 405, 409):
        logger.debug(f"📁 Folder OK: {path}")
        return

    raise Exception(f"❌ MKCOL gagal {path} ({r.status_code})")


# ==================================================
# GET EXISTING SHARE LINK
# ==================================================
def get_existing_share(path, cookies, requesttoken):
    headers = {
        "OCS-APIRequest": "true",
        "requesttoken": requesttoken,
        "Accept": "application/json"
    }

    r = requests.get(
        BASE_OCS + "?format=json",
        headers=headers,
        cookies=cookies,
        params={"path": path}
    )

    if r.status_code != 200:
        return None

    try:
        payload = r.json()
        shares = payload.get("ocs", {}).get("data", [])
        for s in shares:
            if s.get("share_type") == 3 and s.get("url"):
                return s["url"]
    except Exception:
        return None

    return None


# ==================================================
# CREATE SHARE LINK (PUBLIC)
# ==================================================
def create_share(path, cookies, requesttoken):
    headers = {
        "OCS-APIRequest": "true",
        "requesttoken": requesttoken,
        "Accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    r = requests.post(
        BASE_OCS + "?format=json",
        headers=headers,
        cookies=cookies,
        data={
            "path": path,
            "shareType": 3  # public link
        },
        allow_redirects=False
    )

    if r.status_code not in (200, 201):
        raise Exception(f"❌ Create share gagal ({r.status_code})")

    payload = r.json()
    data = payload.get("ocs", {}).get("data")
    if not data or "url" not in data:
        raise Exception("❌ URL share tidak ditemukan")

    return data["url"]


# ==================================================
# GET OR CREATE SHARE (1 FOLDER = 1 LINK)
# ==================================================
def get_or_create_share(path, cookies, requesttoken):
    """
    Pastikan 1 folder hanya punya 1 link
    """
    existing = get_existing_share(path, cookies, requesttoken)
    if existing:
        return existing

    return create_share(path, cookies, requesttoken)
