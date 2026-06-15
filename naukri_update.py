print("SCRIPT STARTED")
import sys, os, time, requests, tempfile
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

print("Downloading resume...")
r = requests.get(RESUME_URL)
print(f"Download status: {r.status_code}")
tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
tmp.write(r.content)
tmp.close()

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
wait = WebDriverWait(driver, 25)

print("Opening Naukri login...")
driver.get("https://www.naukri.com/nlogin/login")
time.sleep(10)

# Enter email
email_field = wait.until(EC.element_to_be_clickable((By.ID, "usernameField")))
email_field.clear()
email_field.send_keys(EMAIL)
print("Email entered!")
time.sleep(2)

# Enter password
password_field = wait.until(EC.element_to_be_clickable((By.ID, "passwordField")))
password_field.clear()
password_field.send_keys(PASSWORD)
print("Password entered!")
time.sleep(2)

# Click login using JavaScript
login_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[@type='submit']")))
driver.execute_script("arguments[0].click();", login_btn)
print("Login clicked via JS!")
time.sleep(10)

print(f"After login URL: {driver.current_url}")

# Check if login succeeded
if "nlogin" in driver.current_url:
    print("❌ Still on login page - trying alternative login...")
    # Try direct JS login
    driver.execute_script(f"""
        document.getElementById('usernameField').value = '{EMAIL}';
        document.getElementById('passwordField').value = '{PASSWORD}';
    """)
    time.sleep(1)
    driver.execute_script("document.querySelector('button[type=submit]').click();")
    time.sleep(10)
    print(f"After retry URL: {driver.current_url}")

print("Going to profile page...")
driver.get("https://www.naukri.com/mnjuser/profile")
time.sleep(8)
print(f"Profile URL: {driver.current_url}")
print(f"Profile title: {driver.title}")

# Scroll down
driver.execute_script("window.scrollTo(0, 800)")
time.sleep(2)

file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
print(f"Found {len(file_inputs)} file inputs")

if file_inputs:
    driver.execute_script("arguments[0].style.display = 'block';", file_inputs[0])
    file_inputs[0].send_keys(tmp.name)
    time.sleep(5)
    print("✅ Resume uploaded!")
else:
    print("❌ Login failed - not authenticated")

driver.quit()
print("✅ Script completed!")
