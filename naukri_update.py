import os, time, requests, tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

EMAIL      = os.environ["NAUKRI_EMAIL"]
PASSWORD   = os.environ["NAUKRI_PASSWORD"]
RESUME_URL = os.environ["RESUME_URL"]

def download_resume():
    r = requests.get(RESUME_URL)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.write(r.content)
    tmp.close()
    return tmp.name

def update_naukri(resume_path):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    wait = WebDriverWait(driver, 15)

    driver.get("https://www.naukri.com/nlogin/login")
    wait.until(EC.presence_of_element_located((By.ID, "usernameField"))).send_keys(EMAIL)
    driver.find_element(By.ID, "passwordField").send_keys(PASSWORD)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(3)

    driver.get("https://www.naukri.com/mnjuser/profile")
    time.sleep(3)
    upload = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
    upload.send_keys(resume_path)
    time.sleep(5)

    print("✅ Naukri profile updated!")
    driver.quit()

resume = download_resume()
update_naukri(resume)