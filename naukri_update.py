print("SCRIPT STARTED")
import sys, os, time, requests, tempfile
print(f"Python: {sys.version}")

EMAIL = os.environ.get("NAUKRI_EMAIL")
PASSWORD = os.environ.get("NAUKRI_PASSWORD")
RESUME_URL = os.environ.get("RESUME_URL")

print(f"EMAIL set: {bool(EMAIL)}")

# Step 1: Download resume
print("Downloading resume...")
r = requests.get(RESUME_URL)
print(f"Download status: {r.status_code}")
tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
tmp.write(r.content)
tmp.close()
print(f"Resume saved: {tmp.name}")

# Step 2: Login via Naukri API
session = requests.Session()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "appid": "109",
    "systemid": "109",
}

print("Logging in via API...")
login_payload = {
    "username": EMAIL,
    "password": PASSWORD,
    "type": "login"
}

login_response = session.post(
    "https://www.naukri.com/central-login-services/v1/login",
    json=login_payload,
    headers=headers
)

print(f"Login status: {login_response.status_code}")
print(f"Login response: {login_response.text[:500]}")

if login_response.status_code == 200:
    login_data = login_response.json()
    print(f"Login data keys: {list(login_data.keys())}")

    # Extract auth token
    token = None
    if "data" in login_data:
        token = login_data["data"].get("authToken") or login_data["data"].get("jwtToken")
    print(f"Token found: {bool(token)}")

    if token:
        # Step 3: Upload resume
        print("Uploading resume...")
        upload_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Authorization": f"Bearer {token}",
            "appid": "109",
            "systemid": "109",
        }

        with open(tmp.name, "rb") as f:
            files = {"file": ("resume.pdf", f, "application/pdf")}
            upload_response = session.post(
                "https://www.naukri.com/profile-services/v1/user/uploadResume",
                files=files,
                headers=upload_headers
            )

        print(f"Upload status: {upload_response.status_code}")
        print(f"Upload response: {upload_response.text[:300]}")

        if upload_response.status_code == 200:
            print("✅ Resume uploaded successfully!")
        else:
            print("❌ Upload failed")
    else:
        print("❌ No token in login response")
else:
    print("❌ Login API failed")

print("✅ Script completed!")
