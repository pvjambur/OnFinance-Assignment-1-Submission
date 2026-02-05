# Mobile Automation Agent - Setup & Run Guide

## 1. System Requirements
Before you begin, ensure you have the following installed:

### Required Software
1.  **Python 3.10+**: [Download Here](https://www.python.org/downloads/)
2.  **Node.js & npm** (for Appium): [Download Here](https://nodejs.org/)
3.  **Android Studio** (for Emulator): [Download Here](https://developer.android.com/studio)
4.  **Tesseract OCR** (for text recognition):
    *   **Windows**: [Installer](https://github.com/UB-Mannheim/tesseract/wiki) (Add to PATH during install!)
    *   **Mac**: `brew install tesseract`
    *   **Linux**: `sudo apt install tesseract-ocr`

### Android Emulator Setup
1.  Open **Android Studio**.
2.  Go to **Device Manager** -> **Create Virtual Device**.
3.  Select a phone (e.g., Pixel 6).
4.  Select a System Image (Recommended: **Android 11.0 or higher**).
5.  Finish and **Launch** the emulator.

---

## 2. Installation Steps

### Step 1: Clone the Repository
```bash
git clone <your-repo-url>
cd mobile-automation-agent
```

### Step 2: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Install Appium & Driver
Appium is the bridge between our code and the Android emulator.
```bash
# Install Appium globally
npm install -g appium

# Install the UIAutomator2 driver (for Android)
appium driver install uiautomator2

# Verify installation
appium driver list
# (It should show 'uiautomator2' as 'installed')
```

### Step 4: Environment Variables
Create a file named `.env` in the root folder (`mobile-automation-agent/.env`) and add your keys:

```ini
# Required for AI Brain
GOOGLE_API_KEY=your_gemini_api_key_here

# Optional: Supabase for Auth Verification
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key

# Optional: Redis for fast caching (if using Docker)
REDIS_URL=redis://localhost:6379/0
```

---

## 3. How to Run

### Step 1: Start the Android Emulator
Make sure your emulator is visible on the screen.

### Step 2: Start Appium Server
Open a **new command prompt/terminal** window and run:
```bash
appium
```
*You should see output starting with `[Appium] Welcome to Appium...`*

### Step 3: Start the Agent
Open another **command prompt/terminal** in the project folder and run:
```bash
python main.py
```

---

## 4. Using the Agent

Once the agent enters the loop, it will speak: **"I am ready."**

### Voice Commands
*   **"Open [App Name]"**: Opens any app (e.g., "Open YouTube", "Open Settings").
*   **"Search for [Item]"**: Taps search and types (e.g., "Search for cute cats").
*   **"Scroll Down/Up"**: Scrolls the page.
*   **"Go Home" / "Go Back"**: Navigation.
*   **"Stop"**: Stops the current task and summarizes what it did.
*   **"Exit"**: Shuts down the agent completely.

### Example Workflow
1.  **You:** "Open YouTube."
2.  **Agent:** "Starting Open YouTube." -> (Opens App) -> "You are on the YouTube Home Screen."
3.  **You:** "Search for MKBHD."
4.  **Agent:** (Typing...) "Typing MKBHD."
5.  **You:** "Stop."
6.  **Agent:** "We opened YouTube and searched for MKBHD. You are on the Results Page."

---

## 5. Troubleshooting Common Issues

### "Could not find 'adb' or 'android'"
*   Ensure **Android SDK Platform-Tools** are in your system PATH.
*   Path usually: `C:\Users\<User>\AppData\Local\Android\Sdk\platform-tools`

### "Tesseract not found"
*   Ensure Tesseract is installed and added to PATH.
*   You may need to restart your terminal after installing.

### "Appium connection refused"
*   Make sure `appium` is running in a separate terminal window BEFORE finding `main.py`.

### "Agent keeps scrolling forever"
*   Say "Stop". The loop detection should allow max 2 scrolls before stopping automatically, but you can always override it.
