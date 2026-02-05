from appium import webdriver
from appium.options.android import UiAutomator2Options
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

USERNAME = os.getenv("BROWSERSTACK_USERNAME")
ACCESS_KEY = os.getenv("BROWSERSTACK_ACCESS_KEY")
HUB_URL = os.getenv("BROWSERSTACK_HUB", "https://hub-cloud.browserstack.com/wd/hub")

print(f"🔌 Testing connection...")
print(f"👤 User: {USERNAME}")
print(f"🔑 Key: {'OK' if ACCESS_KEY else 'MISSING'}")
print(f"🌐 Hub: {HUB_URL}")

options = UiAutomator2Options()

# --- MODIFIED CONFIGURATION ---
bstack_options = {
    "userName": USERNAME,
    "accessKey": ACCESS_KEY,
    "projectName": "Connection Test",
    "buildName": "test-build",
    "sessionName": "Smoke Test",
    # Move device details INSIDE here for better reliability
    "deviceName": "Google Pixel 8 Pro",
    "platformVersion": "14.0"
}

options.set_capability('bstack:options', bstack_options)
options.set_capability('platformName', 'android')
options.set_capability('browserName', 'Chrome') # Chrome is outside

try:
    print("\n⏳ Attempting to connect to BrowserStack (Pixel 8 Pro)...")
    driver = webdriver.Remote(command_executor=HUB_URL, options=options)
    
    print("✅ SUCCESS! Connected to BrowserStack.")
    print(f"📱 Session ID: {driver.session_id}")
    
    print("🌍 Loading Google.com...")
    driver.get("https://google.com")
    print("✅ Page Loaded!")
    
    driver.quit()
except Exception as e:
    print("\n❌ CONNECTION FAILED")
    print("---------------------------------------------------")
    print(e)
    print("---------------------------------------------------")