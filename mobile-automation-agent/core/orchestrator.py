import logging
import time
import sys
from agents.action_agent import action_agent
from agents.auth_agent import auth_agent
from core.screen_analyzer import screen_analyzer
from core.voice_interface import voice
from clients.appium_client import appium_client
from clients.google_genai_client import gemini_client
from clients.supabase_client import supabase_client

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self):
        self.running = False
        self.action_history = []

    def start(self):
        logger.info("🚀 Agent Online")
        appium_client.initialize_driver()
        
        voice.speak("I am ready.")
        self.running = True
        
        while self.running:
            logger.info("🎤 Listening...")
            user_command = voice.listen()
            if not user_command: continue

            if any(kw in user_command.lower() for kw in ["exit", "quit", "terminate"]):
                voice.speak("Goodbye.")
                break

            self.action_history = []
            self.execute_task_fast(user_command)
            
            if not self.running: break
            
            voice.speak("Ready for next command.")

    def execute_task_fast(self, goal: str):
        voice.speak(f"Starting: {goal}")
        
        # Initial Page ID
        appium_client.capture_screenshot("latest.png")
        ocr_results = screen_analyzer.extract_text("latest.png")
        self.identify_page(ocr_results, initial=True)
        
        for step in range(1, 15):
            logger.info(f"--- Step {step} ---")
            
            # [CHECK 1] STOP BETWEEN STEPS (Crucial for your request)
            if self.check_interrupt(ocr_results): return

            if step > 1:
                appium_client.capture_screenshot("latest.png")
                ocr_results = screen_analyzer.extract_text("latest.png")
            
            screen_state = {"ocr_results": ocr_results}
            
            # Login Check
            if auth_agent.is_login_screen(screen_state):
                self.handle_auth_flow(screen_state)
                continue

            # AI Plan
            plan = action_agent.run(goal, screen_state)
            action = plan.get('action')
            target = plan.get('target_text')
            val = plan.get('value')
            reason = plan.get('reason')

            # Narrate
            if reason:
                voice.speak(reason)
            else:
                if action == 'tap': voice.speak(f"Tapping {target}.")
                elif action == 'input': voice.speak(f"Typing {val}.")
                elif action == 'scroll': voice.speak("Scrolling.")
                elif action == 'system': voice.speak(f"System {val}.")
                elif action == 'finish':
                    voice.speak("Task complete.")
                    self.summarize_session(ocr_results)
                    return

            # [CHECK 2] STOP BEFORE ACTION
            if self.check_interrupt(ocr_results): return

            # Execute Action
            final_action = {"type": action, "value": val, "target": target}
            if action == 'tap':
                coords = screen_analyzer.find_text_coordinates(target, ocr_results)
                if coords: final_action['coordinates'] = coords
            
            appium_client.execute_action(final_action)
            
            # Update History
            current_sig = f"{action}:{target}:{val}"
            self.action_history.append(current_sig)

            # [CHECK 3] STOP AFTER ACTION
            if self.check_interrupt(ocr_results): return

            # Periodic Summary (Every 2 Steps)
            if step % 2 == 0:
                self.summarize_session(ocr_results, periodic=True)

            # Loop Detection
            if len(self.action_history) >= 2:
                if self.action_history[-1] == self.action_history[-2]:
                    is_safe = any(x in current_sig for x in ['volume', 'scroll'])
                    if not is_safe:
                        logger.warning("🔄 Loop Detected.")
                        voice.speak("I am stuck. Stopping now.")
                        self.summarize_session(ocr_results) 
                        return 

    def check_interrupt(self, ocr_results=None):
        """Fast check (0.5s) to catch 'Stop' between steps"""
        interrupt = voice.listen(timeout=0.5)
        
        if interrupt:
            text = interrupt.lower()
            
            if any(kw in text for kw in ["exit", "quit"]):
                 voice.speak("Exiting agent.")
                 self.running = False 
                 return True
            
            elif any(kw in text for kw in ["stop", "wait"]):
                 voice.speak("Stopping task.")
                 self.summarize_session(ocr_results)
                 return True 
                 
        return False

    def handle_auth_flow(self, screen_state):
        logger.info("🔒 Login Detected")
        voice.speak("Login detected. Say username.")
        
        username = voice.listen(timeout=8)
        if not username: return

        voice.speak("Say password.")
        password = voice.listen(timeout=8)
        if not password: return
             
        voice.speak("Verifying...")
        is_valid, msg = supabase_client.verify_user(username, password)
        
        if is_valid:
            voice.speak("Verified. Logging in.")
        else:
            voice.speak(f"Verification failed: {msg}. Type anyway?")
            if "yes" not in (voice.listen(timeout=5) or "").lower(): return

        appium_client.execute_action({"type": "input", "value": username})
        appium_client.execute_action({"type": "system", "command": "enter"})
        appium_client.execute_action({"type": "input", "value": password})
            
        ocr_results = screen_state.get('ocr_results', [])
        submit_btn = screen_analyzer.find_text_coordinates("Sign In", ocr_results) or \
                     screen_analyzer.find_text_coordinates("Log In", ocr_results) or \
                     screen_analyzer.find_text_coordinates("Next", ocr_results)
                     
        if submit_btn:
            appium_client.execute_action({"type": "tap", "coordinates": submit_btn})
        else:
            appium_client.execute_action({"type": "system", "command": "enter"})

    def identify_page(self, ocr_results, initial=False):
        visible_text = [item['text'] for item in ocr_results]
        prompt = f"Identify the screen based on text: {visible_text[:30]}. Return ONLY the page name."
        try:
            page_name = gemini_client.generate_text(prompt).strip()
            if initial: voice.speak(f"You are on the {page_name}.")
            return page_name
        except: return "Unknown Page"

    def summarize_session(self, ocr_results=None, periodic=False):
        if not self.action_history: return
        
        visible_text = []
        if ocr_results:
             visible_text = [item['text'] for item in ocr_results]
        elif hasattr(screen_analyzer, 'extract_text'):
             res = screen_analyzer.extract_text("latest.png")
             visible_text = [item['text'] for item in res]
             
        prompt = f"""
        Actions: {self.action_history}
        Screen: {visible_text[:30]} 
        Summarize what was done in 1 sentence.
        RESPONSE JSON: {{ "summary": "...", "current_page": "..." }}
        """
        try:
            result = gemini_client.generate_json(prompt=prompt)
            summary = result.get('summary', 'Done.')
            page = result.get('current_page', 'page')
            
            if periodic:
                voice.speak(f"Update: {summary}")
            else:
                voice.speak(f"Summary: {summary}. You are on the {page}.")
        except:
            voice.speak("Task update.")

orchestrator = Orchestrator()