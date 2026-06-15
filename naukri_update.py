print("SCRIPT STARTED")
import sys, os, time, requests, tempfile
print(f"Python: {sys.version}")

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

EMAIL = os.environ.get("NAUKRI_EMAIL")
PASSWORD = os.environ.get("NAUKRI_PASSWORD")
RESUME_URL = os.environ.get("RESUME_URL")

print(f"EMAIL set: {bool(EMAIL)}")
print(f"RESUME_URL: {RESUME_URL}")

print("Downloading resume...")
r = requests.get(RESUME_URL)
print(f"Download status: {r.status_code}")
tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
tmp.write(r.content)
tmp.close()
print(f"Resume saved: {tmp.name}")

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

print("Starting Chrome...")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
wait = WebDriverWait(driver, 25)
print("Chrome started!")

print("Opening Naukri login...")
driver.get("https://www.naukri.com/nlogin/login")
time.sleep(10)
print(f"Title: {driver.title}")

inputs = driver.find_elements(By.TAG_NAME, "input")
for inp in inputs:
    if inp.get_attribute('type') in ['text', 'email'] and inp.is_displayed():
        inp.click()
        time.sleep(1)
        inp.send_keys(EMAIL)
        print("Email entered!")
        break

for inp in inputs:
    if inp.get_attribute('type') == 'password' and inp.is_displayed():
        inp.click()
        time.sleep(1)
        inp.send_keys(PASSWORD)
        print("Password entered!")
        break

login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(@class,'login-btn') or contains(text(),'Login') or @type='submit']")))
login_btn.click()
print("Login clicked!")
time.sleep(10)
print(f"After login URL: {driver.current_url}")

driver.get("https://www.naukri.com/mnjuser/profile")
time.sleep(8)
print(f"Profile URL: {driver.current_url}")
print(f"Profile title: {driver.title}")

# Scroll down to find resume section
driver.execute_script("window.scrollTo(0, 500)")
time.sleep(2)

# Try multiple ways to find file input
file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
print(f"Found {len(file_inputs)} file inputs")

if not file_inputs:
    # Try clicking the update resume button first
    try:
        update_btn = driver.find_element(By.XPATH, "//span[contains(text(),'Update resume')] | //a[contains(text(),'Update')] | //button[contains(text(),'Update')]")
        update_btn.click()
        print("Clicked update resume button!")
        time.sleep(3)
        file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
        print(f"After click: Found {len(file_inputs)} file inputs")
    except Exception as e:
        print(f"Update button not found: {e}")

if file_inputs:
    driver.execute_script("arguments[0].style.display = 'block';", file_inputs[0])
    file_inputs[0].send_keys(tmp.name)
    time.sleep(5)
    print("✅ Resume uploaded!")
else:
    print("❌ No file input found — saving page source for debug")
    with open("/tmp/profile_page.html", "w") as f:
        f.write(driver.page_source)
    print("Page source saved")

driver.quit()
print("✅ Done!")
