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

def download_resume():
    print("Downloading resume...")
    r = requests.get(RESUME_URL)
    print(f"Resume download status: {r.status_code}")
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    tmp.write(r.content)
    tmp.close()
    print(f"Resume saved: {tmp.name}")
    return tmp.name

def update_naukri(resume_path):
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--window-size=1920,1080")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    print("Starting Chrome...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    print("Chrome started!")

    wait = WebDriverWait(driver, 25)

    print("Opening Naukri...")
    driver.get("https://www.naukri.com/nlogin/login")
    time.sleep(10)
    print(f"Title: {driver.title}")
    print(f"URL: {driver.current_url}")

    # Print all input fields found on page
    inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"Found {len(inputs)} input fields:")
    for i, inp in enumerate(inputs):
        print(f"  [{i}] type={inp.get_attribute('type')} id={inp.get_attribute('id')} placeholder={inp.get_attribute('placeholder')} visible={inp.is_displayed()}")

    print("Entering email...")
    for inp in inputs:
        if inp.get_attribute('type') in ['text', 'email'] and inp.is_displayed():
            inp.click()
            time.sleep(1)
            inp.send_keys(EMAIL)
            print("Email entered!")
            break

    print("Entering password...")
    for inp in inputs:
        if inp.get_attribute('type') == 'password' and inp.is_displayed():
            inp.click()
