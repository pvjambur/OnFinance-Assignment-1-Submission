# 🚀 Run Guide: Mobile Automation Agent

This guide explains how to run the agent, integrate with Appium, and use the "Free Stack".

## 1. Prerequisites (Done? Check!)
- [x] Python 3.11+
- [x] `.env` filled with API keys
- [x] Supabase Database setup (Review `supabase/README.md`)

## 2. Choosing Your Mode

### Mode A: Voice Agent (CLI) 🗣️
This is the main interactive mode. It listens to your microphone and talks back.
```bash
# Run from root folder
python main.py
```
*   **What it does**: Starts the `Orchestrator` loop. Listens -> Thinks -> Acts.
*   **Best for**: Local testing, demos.

### Mode B: API Server 🌐
Run this if you want to control the agent via HTTP or build a Frontend.
```bash
python run_api.py
```
*   **What it does**: Starts FastAPI on `http://localhost:8000`.
*   **Docs**: Go to `http://localhost:8000/docs` to see Swagger UI.

## 3. Appium & Device Integration 📱

### Option A: BrowserStack (Cloud - Recommended)
The project is pre-configured for BrowserStack.
1.  Set `BROWSERSTACK_USERNAME` and `BROWSERSTACK_ACCESS_KEY` in `.env`.
2.  The `clients/browserstack.py` handles uploading apps.
3.  The `ActionExecutor` (core/action_executor.py) will connect to the BS Hub defined in `settings.py`.

### Option B: Local Android Emulator (Free)
1.  Install Android Studio & create an AVD (Emulator).
2.  Start the emulator.
3.  Start the Appium Server locally:
    ```bash
    appium
    ```
4.  Update `.env` (or code) to point `BROWSERSTACK_HUB` to `http://localhost:4723`.

## 4. Duplicate Files Explanation
You noticed `main.py` vs `api/main.py`. This is standard pattern:
*   `main.py` (Root): The Entry Point for the **User Application** (Voice Agent).
*   `api/main.py`: The Entry Point for the **Web Server** (FastAPI).
*   `run_api.py`: A helper script specifically to launch `api/main.py`.

## 5. Deployment (Docker) 🐳
To run everything (Agent + Redis) in containers:
```bash
docker-compose up --build
```

## 6. Testing 🧪
Run the included tests to verify logic without real devices:
```bash
pytest tests/
```
