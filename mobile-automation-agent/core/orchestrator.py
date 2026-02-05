import logging
import time
from typing import Dict, Any

from agents.intent_agent import intent_agent
from agents.action_agent import action_agent
from agents.auth_agent import auth_agent
from core.screen_analyzer import screen_analyzer
from core.voice_interface import voice
from clients.appium_client import appium_client
from clients.google_genai_client import gemini_client

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self):
        self.running = False
        self.action_history = []

    def start(self):
        logger.info("🚀 Mobile Agent Online (Continuous Mode)")
        appium_client.initialize_driver()
        
        voice.speak("I am online. What should I do?")
        self.running = True
        
        while self.running:
            # 1. ALWAYS LISTEN (The Main Loop)
            logger.info("🎤 Listening for command...")
            user_command = voice.listen()
            
            if not user_command: 
                continue

            # Global Exit Command
            if "exit" in user_command.lower() or "terminate" in user_command.lower():
                voice.speak("Shutting down.")
                break

            # 2. Execute Task
            self.action_history = []
            self.execute_task_fast(user_command)
            
            # After task finishes, loop back to Step 1 automatically
            voice.speak("I am ready for the next command.")

    def execute_task_fast(self, goal: str):
        voice.speak(f"Starting: {goal}")
        
        # We run up to 15 steps, but we check for "STOP" every time
        for step in range(1, 15):
            logger.info(f"--- Step {step} ---")
            
            # A. SCREENSHOT (Taking a fresh look every step)
            screenshot = appium_client.capture_screenshot("latest.png")
            if not screenshot:
                logger.error("❌ Screenshot failed. Retrying...")
                time.sleep(1)
                continue

            # B. FAST OCR
            ocr_results = screen_analyzer.extract_text("latest.png")
            screen_state = {"ocr_results": ocr_results}
            
            # C. SECURITY CHECK: IS THIS A LOGIN SCREEN?
            # We run the AuthAgent BEFORE the ActionAgent
            is_login = auth_agent.is_login_screen(screen_state)
            if is_login:
                self.handle_auth_flow(screen_state)
                # After handling login, we capture a new screenshot and restart the step
                continue 

            # D. ACTION PLANNING
            plan = action_agent.run(goal, screen_state)
            
            action_type = plan.get('action')
            target_text = plan.get('target_text')
            input_value = plan.get('value')
            
            # E. STOP CHECK
            # We can't "listen" while thinking, but if the AI decides to "wait",
            # or if we implement a separate listen thread (complex), 
            # for now, we rely on the user saying "Stop" if prompted.
            if action_type == 'finish':
                voice.speak("Task complete.")
                self.summarize_session()
                return # Go back to main loop

            # F. VOICE FEEDBACK & EXECUTION
            if action_type == 'tap':
                voice.speak(f"Tapping {target_text or 'screen'}")
                final_action = {"type": "tap", "target": target_text}
                
                # Resolve coordinates locally (FAST)
                if target_text:
                    coords = screen_analyzer.find_text_coordinates(target_text, ocr_results)
                    if coords:
                        final_action['coordinates'] = coords
                
                appium_client.execute_action(final_action)

            elif action_type == 'input':
                voice.speak(f"Typing {input_value}")
                appium_client.execute_action({"type": "input", "value": input_value})
                
            elif action_type == 'scroll':
                voice.speak("Scrolling")
                appium_client.execute_action({"type": "scroll"})

            # Log history
            self.action_history.append(f"{action_type} on {target_text or 'screen'}")
            
            # G. RESPONSIVENESS CHECK: Check for STOP command
            # This replaces time.sleep(1) with a useful listen check.
            logger.info("👂 Checking for stop...")
            interrupt = voice.listen(timeout=1)
            if interrupt and ("stop" in interrupt.lower() or "wait" in interrupt.lower()):
                 voice.speak("Stopping as requested.")
                 self.summarize_session()
                 return # Exit task loop, go back to main listening loop

 

    def handle_auth_flow(self, screen_state):
        """
        Pauses execution to ask the user for credentials securely.
        """
        logger.info("🔒 Login Screen Detected - Intercepting Control")
        voice.speak("I see a login screen. I need your help.")
        
        # 1. Ask for ID
        voice.speak("Please say your username or email.")
        username = voice.listen()
        if username:
            voice.speak(f"Entering username.")
            # We assume focus is on the field or we tap the first input found
            appium_client.execute_action({"type": "input", "value": username})
            time.sleep(1)

        # 2. Ask for Password
        voice.speak("Please say your password.")
        password = voice.listen()
        if password:
            voice.speak("Entering password.")
            appium_client.execute_action({"type": "input", "value": password})
            time.sleep(1)
            
        # 3. Submit
        voice.speak("Attempting to sign in.")
        # Try to find a "Sign In" or "Login" button specifically
        ocr_results = screen_state.get('ocr_results', [])
        submit_btn = screen_analyzer.find_text_coordinates("Sign In", ocr_results) or \
                     screen_analyzer.find_text_coordinates("Log In", ocr_results) or \
                     screen_analyzer.find_text_coordinates("Next", ocr_results)
                     
        if submit_btn:
            appium_client.execute_action({"type": "tap", "coordinates": submit_btn})
        else:
            # Fallback: Press Enter key via ADB
            appium_client.execute_action({"type": "input", "value": "\\n"})

    def summarize_session(self):
        if not self.action_history: return
        summary = gemini_client.generate_text(f"Summarize these actions for a blind user: {self.action_history}")
        voice.speak(summary)

    def summarize_and_stop(self):
        voice.speak("Stopping.")
        self.running = False

orchestrator = Orchestrator()