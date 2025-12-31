import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def login_drive_get_session(username, password):
    options = Options()
    options.add_argument("--start-maximized")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    wait = WebDriverWait(driver, 30)

    driver.get("https://drive.bps.go.id")
    sso_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(text(), 'Single Sign-On BPS')]")
        )
    )
    sso_btn.click()

    wait.until(EC.presence_of_element_located((By.ID, "username"))).send_keys(username)
    wait.until(EC.presence_of_element_located((By.ID, "password"))).send_keys(password)
    driver.find_element(By.ID, "kc-login").click()

    wait.until(EC.url_contains("drive.bps.go.id"))
    time.sleep(3)

    cookies = {c["name"]: c["value"] for c in driver.get_cookies()}
    requesttoken = driver.execute_script(
        "return window.oc_requesttoken || (window.OC && OC.requestToken);"
    )
    driver.quit()

    if not requesttoken:
        raise Exception("requesttoken tidak ditemukan")

    user_id = cookies.get("nc_username")
    if not user_id:
        raise Exception("USER_ID tidak ditemukan")

    return cookies, requesttoken, user_id
