import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from config import USERNAME, PASSWORD


def login_and_get_xauth():
    options = Options()
    options.add_argument("--start-maximized")
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    wait = WebDriverWait(driver, 30)

    print("🔐 Login KipApp...")
    driver.get("https://kipapp.bps.go.id/#/auth/login")

    login_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[.//span[text()='Login SSO']]")
        )
    )
    login_btn.click()

    wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(USERNAME)
    wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys(PASSWORD)
    driver.find_element(By.ID, "kc-login").click()

    wait.until(EC.url_contains("kipapp.bps.go.id"))
    time.sleep(3)

    driver.get("https://kipapp.bps.go.id/api/v1/user")
    time.sleep(2)

    token = None
    for entry in driver.get_log("performance"):
        msg = json.loads(entry["message"])["message"]
        if msg["method"] == "Network.requestWillBeSent":
            headers = msg["params"]["request"].get("headers", {})
            if "X-Auth" in headers:
                token = headers["X-Auth"]
                break

    driver.quit()

    if not token:
        raise Exception("❌ X-Auth gagal diambil")

    print("✅ X-Auth berhasil")
    return token
