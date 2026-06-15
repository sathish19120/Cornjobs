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
    time.sleep(5)
    print(f"Page title: {driver.title}")
    print(f"Page URL: {driver.current_url}")

    print("Finding email field...")
    try:
        email_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='text' or @type='email']")))
        email_field.clear()
        email_field.send_keys(EMAIL)
        print("Email entered!")
    except Exception as e:
        print(f"Email field error: {e}")
        driver.save_screenshot("/tmp/login_error.png")
        raise

    print("Finding password field...")
    password_field = driver.find_element(By.XPATH, "//input[@type='password']")
    password_field.clear()
    password_field.send_keys(PASSWORD)
    print("Password entered!")

    print("Clicking login button...")
    login_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
    login_btn.click()
    time.sleep(5)
    print(f"After login URL: {driver.current_url}")
    print("Logged in!")

    print("Going to profile page...")
    driver.get("https://www.naukri.com/mnjuser/profile")
    time.sleep(5)

    print("Uploading resume...")
    upload = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
    upload.send_keys(resume_path)
    time.sleep(5)

    print("✅ Naukri profile updated!")
    driver.quit()

resume = download_resume()
update_naukri(resume)
