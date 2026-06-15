print("SCRIPT STARTED")
import sys, os, time, requests, tempfile, json
print(f"Python: {sys.version}")

EMAIL = os.environ.get("NAUKRI_EMAIL")
PASSWORD = os.environ.get("NAUKRI_PASSWORD")
RESUME_URL = os.environ.get("RESUME_URL")

# Download resume
print("Downloading resume...")
r = requests.get(RESUME_URL)
print(f"Download status: {r.status_code}")
tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
tmp.write(r.content)
tmp.close()
print(f"Resume saved: {tmp.name}")

# Login via session
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.naukri.com/nlogin/login",
    "Origin": "https://www.naukri.com",
    "appid": "109",
    "systemid": "jobseeker",
    "Content-Type": "application/json",
})

print("Logging in...")
login_resp = session.post(
    "https://www.naukri.com/central-login-services/v1/login",
    json={"username": EMAIL, "password": PASSWORD, "type": "login"},
)
print(f"Login status: {login_resp.status_code}")
print(f"Login response: {login_resp.text[:1000]}")

data = login_resp.json()

# Try to find token anywhere in response
token = None
nauthtoken = None

if "data" in data:
    d = data["data"]
    token = d.get("authToken") or d.get("jwtToken") or d.get("token")
    nauthtoken = d.get("nauthtoken") or d.get("nAuthToken")
    print(f"User ID: {d.get('userId') or d.get('id')}")

print(f"Token: {bool(token)}")
print(f"NAuthToken: {bool(nauthtoken)}")
print(f"Cookies: {dict(session.cookies)}")

if not token and not nauthtoken:
    print("No token found — trying cookie-based upload")

# Upload resume using cookies from login
print("Uploading resume...")
upload_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json",
    "appid": "109",
    "systemid": "jobseeker",
    "Referer": "https://www.naukri.com/mnjuser/profile",
}

if token:
    upload_headers["Authorization"] = f"Bearer {token}"
if nauthtoken:
    upload_headers["nauthtoken"] = nauthtoken

with open(tmp.name, "rb") as f:
    upload_resp = session.post(
        "https://www.naukri.com/profile-services/v1/user/uploadResume",
        files={"file": ("resume.pdf", f, "application/pdf")},
        headers=upload_headers
    )

print(f"Upload status: {upload_resp.status_code}")
print(f"Upload response: {upload_resp.text[:500]}")

if upload_resp.status_code == 200:
    print("✅ Resume uploaded successfully!")
else:
    print("❌ Upload failed - check response above")

print("✅ Done!")
