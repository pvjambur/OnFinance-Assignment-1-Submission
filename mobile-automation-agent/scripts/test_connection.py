import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import settings
import google.generativeai as genai

def test_google():
    print("Testing Google Gemini...", end=" ")
    if not settings.GOOGLE_API_KEY:
        print("SKIP (No Key)")
        return
        
    try:
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Say hello")
        if response.text:
            print("✅ OK")
        else:
            print("❌ Failed (Empty)")
    except Exception as e:
        print(f"❌ Failed ({e})")

def test_dirs():
    print("Testing Directories...", end=" ")
    if settings.AGENT_CONFIG_DIR.exists():
        print("✅ OK")
    else:
        print(f"❌ Failed ({settings.AGENT_CONFIG_DIR} missing)")

def main():
    print("Running Connection Tests...\n")
    test_dirs()
    test_google()
    print("\nDone.")

if __name__ == "__main__":
    main()
