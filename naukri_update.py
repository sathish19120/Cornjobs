print("SCRIPT STARTED")
import sys
print(f"Python version: {sys.version}")

try:
    import os, time, requests, tempfile
    print("Basic imports OK")
    
    from selenium import webdriver
    print("Selenium imported OK")
    
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    print("Selenium modules OK")
    
    from webdriver_manager.chrome import ChromeDriverManager
    print("WebDriverManager OK")

    EMAIL      = os.environ.get("NAUKRI_EMAIL")
    PASSWORD   = os.environ.get("NAUKRI_PASSWORD")
    RESUME_URL = os.environ.get("RESUME_URL")
    print(f"EMAIL set: {bool(EMAIL)}")
    print(f"PASSWORD set: {bool(PASSWORD)}")
    print(f"RESUME_URL set: {bool(RESUME_URL)}")

    print("Downloading resume...")
    r = requests.get(RESUME_URL)
    print(f"Resume download status: {r.status_code}")
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
    print("Chrome started!")

    wait = WebDriverWait(driver, 25)

    print("Opening Naukri login page...")
    driver.get("https://www.naukri.com/nlogin/login")
    time.sleep(10)
    print(f"Title: {driver.title}")
    print(f"URL: {driver.current_url}")

    inputs = driver.find_elements(By.TAG_NAME, "input")
    print(f"Found {len(inputs)} input fields:")
    for i, inp in enumerate(inputs):
        print(f"  [{i}] type={inp.get_attribute('type')} id={inp.get_attribute('id')} placeholder={inp.get_attribute('placeholder')} visible={inp.is_displayed()}")

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

    buttons = driver.find_elements(By.TAG_NAME, "button")
    for btn in buttons:
        if btn.is_displayed() and btn.get_attribute('type') == 'submit':
            btn.click()
            print("Login clicked!")
            break

    time.sleep(8)
    print(f"After login URL: {driver.current_url}")

    driver.get("https://www.naukri.com/mnjuser/profile")
    time.sleep(5)

    file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
    print(f"Found {len(file_inputs)} file inputs")

    if file_inputs:
        file_inputs[0].send_keys(tmp.name)
        time.sleep(5)
        print("✅ Resume uploaded successfully!")
    else:
        print("❌ No file input found")

    driver.quit()

except Exception as e:
    import traceback
    print(f"❌ ERROR: {e}")
    traceback.print_exc()
    sys.exit(1)
