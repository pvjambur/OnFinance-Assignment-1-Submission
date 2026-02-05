# 📱 AI Mobile Automation Agent (Local + Voice + Vision)

This is a cutting-edge **AI-powered Mobile Automation Agent** that allows you to control Android apps using **Voice Commands**. It runs completely locally (Appium + Emulator) for maximum speed and privacy, using **Google Gemini 2.0 Flash** as the brain and **Tesseract OCR** as the eyes.

## 🚀 Features

-   **🗣️ Voice & Text Control**: Just speak "Open Settings" or "Swipe right".
-   **⚡ "Fast Loop" Architecture**: Optimized for speed. Does NOT rely on slow AI vision for every step. Uses local OCR for instant coordinate mapping.
-   **🧠 Intelligent Orchestrator**: The agent listens continuously, executes tasks, and provides voice feedback.
-   **🔒 Secure Login Handling**: Automatically detects login screens and securely asks for inputs.
-   **📝 Usage Summaries**: Generates a natural language summary of your session when you say "Stop".

---

## 🛠️ Architecture & Evolution

We iterated through several approaches to achieve the best performance:

### Phase 1: BrowserStack / LambdaTest (Cloud)
*   **Attempt:** We started by connecting to cloud device farms (BrowserStack/LambdaTest).
*   **Result:** ❌ **Too Slow**. The network latency (sending screenshots to cloud, getting actions back) made the agent unusable for real-time interaction (20+ seconds per step).

### Phase 2: Pure Vision AI (Gemini Vision)
*   **Attempt:** We sent every screenshot to Gemini Vision to ask for coordinate points.
*   **Result:** ❌ **Inaccurate & Slow**. LLMs are great at reasoning but bad at exact pixel coordinates. They often hallucinates buttons or missed small targets.

### Phase 3: The "Fast Loop" (Current Local Setup) ✅
*   **Solution:** We moved to a Hybrid "Fast Loop" approach:
    1.  **Local Appium**: Runs the emulator on `localhost` (0 latency).
    2.  **Local OCR (Tesseract)**: Instantly finds text location on the screen.
    3.  **Semantic Brain (Gemini)**: The AI simply decides *WHAT* to click (e.g., "Settings"), and Python instantly finds *WHERE* it is.
    
**Result:** ⚡ **10x Faster**. Actions happen in seconds.

---

## 📂 Project Structure

```bash
📦 mobile-automation-agent
 ┣ 📂 agents                  # The "Brain" Components (Modular)
 ┃ ┣ 📜 action_agent.py       # General Planner & Action Router
 ┃ ┣ 📜 auth_agent.py         # 🔒 Security Interceptor (Login Detection)
 ┃ ┣ 📜 typing_agent.py       # ⌨️ Dedicated Typing Logic (Input/Clear)
 ┃ ┣ 📜 navigation_agent.py   # 🧭 Navigation (Scroll, Swipe, Home, Back)
 ┃ ┣ 📜 vision_agent.py       # 👁️ Advanced Screen Analysis
 ┃ ┣ 📜 settings_agent.py     # ⚙️ Toggles (Wifi/Bluetooth/Volume)
 ┃ ┗ 📜 validation_agent.py   # ✅ Success Verification
 ┣ 📂 core                    # Core Infrastructure
 ┃ ┣ 📜 orchestrator.py       # The "Main Loop" (Listen -> Think -> Act)
 ┃ ┣ 📜 screen_analyzer.py    # The "Eyes" (Local Tesseract OCR)
 ┃ ┗ 📜 voice_interface.py    # Whisper (STT) and pyttsx3 (TTS)
 ┣ 📂 clients                 # External Connections
 ┃ ┣ 📜 appium_client.py      # Controls the Android Emulator
 ┃ ┗ 📜 google_genai_client.py # Connects to Gemini API
 ┣ 📜 main.py                 # Entry Point
 ┗ 📜 requirements.txt        # Dependencies
```

---

## 🚀 How to Run
### 1. Prerequisites
-   **Python 3.10+**
-   **Android Studio** (with an Emulator running)
-   **Appium Server** (`npm install -g appium` -> `appium`)
-   **Tesseract OCR** (Installed & Added to PATH)

### 2. Setup
```bash
# Clone
git clone <repo>
cd mobile-automation-agent

# Install Python Deps
pip install -r requirements.txt

# Create .env
echo "GOOGLE_API_KEY=your_key_here" > .env
```

### 3. Run
1.  Start your Android Emulator.
2.  Start Appium in a separate terminal:
    ```bash
    appium
    ```
3.  Run the Agent:
    ```bash
    python main.py
    ```

### 4. Commands
-   **"Open YouTube"**
-   **"Search for Cats"**
-   **"Swipe Down"**
-   **"Stop"** (Generates a summary)
-   **"Exit"** (Shuts down)

---

## 🧩 Key Technologies

## 🧩 Key Technologies

| Component | Tech Used | Role |
| :--- | :--- | :--- |
| **LLM** | Google Gemini 2.0 Flash | Reasoning & Planning |
| **Vision/OCR** | Tesseract (Local) | Text Coordinate Mapping |
| **Data Storage** | Supabase (PostgreSQL) | Logging sessions & user preferences |
| **Driver** | Appium + UiAutomator2 | Android Control |
| **Voice** | SpeechRecognition + Pyttsx3 | User Interface |

---

## ✨ Author
**Pranav V Jambur**  
R. V. College of Engineering  
`pranavvjambur.cs23@rvce.edu.in`
