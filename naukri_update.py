import os, time, requests, tempfile
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

EMAIL      = os.environ.get("NAUKRI_EMAIL")
PASSWORD   = os.environ.get("NAUKRI_PASSWORD")
RESUME_URL = os.environ.get("RESUME_URL")

print(f"EMAIL set: {bool(EMAIL)}")
print(f"PASSWORD set: {bool(PASSWORD)}")

def download_resume():
    print("Downloading resume...")
    r = requests.get(RESUME_URL)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.write(r.content)
    tmp.close()
    print(f"Resume saved to: {tmp.name}")
    return tmp.name

def update_naukri(resume_path):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    print("Starting Chrome...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    print("Chrome started!")

    wait = WebDriverWait(driver, 20)

    print("Opening Naukri login page...")
    driver.get("https://www.naukri.com/nlogin/login")
    time.sleep(8)
    print(f"Page title: {driver.title}")

    print("Finding email field...")
    # Wait for visible and interactable email field
    email_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Enter your active Email ID / Username']")))
    email_field.click()
    time.sleep(1)
    email_field.send_keys(EMAIL)
    print("Email entered!")

    print("Finding password field...")
    password_field = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Enter your password']")))
