import logging
import time
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
            
            if not self.running: break # Exit immediately if "exit" was spoken during task
            
            voice.speak("Ready for next command.")

    def execute_task_fast(self, goal: str):
        voice.speak(f"Starting: {goal}")
        
        # Initial Page Identification
        appium_client.capture_screenshot("latest.png")
        ocr_results = screen_analyzer.extract_text("latest.png")
        self.identify_page(ocr_results, initial=True)
        
        for step in range(1, 15):
            logger.info(f"--- Step {step} ---")
            
            # 1. Screenshot & OCR (Refresh if not first step or modified)
            if step > 1:
                appium_client.capture_screenshot("latest.png")
                ocr_results = screen_analyzer.extract_text("latest.png")
            
            screen_state = {"ocr_results": ocr_results}
            
            # 2. Login Check (Security Interceptor)
            # Automatic detection is enabled here at every step.
            if auth_agent.is_login_screen(screen_state):
                self.handle_auth_flow(screen_state)
                continue

            # 3. AI Plan
            plan = action_agent.run(goal, screen_state)
            action = plan.get('action')
            target = plan.get('target_text')
            val = plan.get('value')

            # 4. Prepare Action & Voice Feedback
            final_action = {"type": action, "value": val, "target": target}
            
            if action == 'tap':
                voice.speak(f"Tapping {target}")
                coords = screen_analyzer.find_text_coordinates(target, ocr_results)
                if coords: final_action['coordinates'] = coords
                
            elif action == 'system':
                # clearer voice for system commands
                if 'volume' in str(val):
                    voice.speak(f"Adjusting volume.")
                elif 'home' in str(val):
                    voice.speak("Going home.")
                else:
                    voice.speak(f"System: {val}")
                    
            elif action == 'input':
                voice.speak(f"Typing {val}")
                
            elif action == 'scroll':
                voice.speak("Scrolling down.")
                
            elif action == 'finish':
                voice.speak("Task done.")
                self.summarize_session(ocr_results)
                return

            # 5. Interrupt Check (Before Action)
            if self.check_interrupt(ocr_results): return

            # 6. Execute
            appium_client.execute_action(final_action)
            
            # 7. Periodic Summary (Every 2 Steps)
            current_sig = f"{action}:{target}:{val}"
            self.action_history.append(current_sig)
            
            if step % 2 == 0:
                self.summarize_session(ocr_results, periodic=True)
            
            # 8. Loop Detection (Stops if SAME action happens 2 times)
            if len(self.action_history) >= 2:
                last_move = self.action_history[-1]
                prev_move = self.action_history[-2]
                
                # Check if identical
                if last_move == prev_move:
                    is_safe_repeat = any(x in last_move for x in ['volume', 'scroll', 'input'])
                    
                    # Allow max 4 repeats for safe actions, 0 for others
                    repeat_count = 0
                    if is_safe_repeat:
                        # Count how many times this specific action has appeared at the end
                        for act in reversed(self.action_history):
                            if act == last_move: repeat_count += 1
                            else: break
                    
                    if not is_safe_repeat or repeat_count >= 2:
                        logger.warning(f"🔄 Loop Detected ({repeat_count} repeats). Stopping.")
                        voice.speak("I seem to be stuck. Stopping task.")
                        self.summarize_session(ocr_results)
                        return
            # 9. Interrupt Check (After Action)
            if self.check_interrupt(ocr_results): return

    def check_interrupt(self, ocr_results=None):
        """Quick check for stop/exit command (1s wait)"""
        logger.info("👂 Checking for stop...")
        interrupt = voice.listen(timeout=1)
        
        if interrupt:
            text = interrupt.lower()
            if any(kw in text for kw in ["exit", "quit", "terminate"]):
                 voice.speak("Exiting agent.")
                 self.running = False
                 return True
            elif any(kw in text for kw in ["stop", "wait"]):
                 voice.speak("Stopping task.")
                 self.summarize_session(ocr_results)
                 return True
                 
        return False


    def handle_auth_flow(self, screen_state):
        """
        Secure Interactive Login Flow with Supabase Verification
        """
        logger.info("🔒 Login Detected")
        voice.speak("I see a login screen. Please say your email or username.")
        
        # 1. Get Username/Email
        username = voice.listen(timeout=8)
        if not username:
            voice.speak("No input detected. Skipping login.")
            return

        voice.speak(f"Got it. Please say your password.")

        # 2. Get Password
        password = voice.listen(timeout=8)
        if not password:
             voice.speak("No password detected. Skipping.")
             return
             
        # 3. Verify with Supabase
        voice.speak("Verifying credentials...")
        is_valid, msg = supabase_client.verify_user(username, password)
        
        if is_valid:
            voice.speak("Credentials verified! Logging in.")
        else:
            voice.speak(f"Warning: Verification failed: {msg}. Type anyway?")
            confirm = voice.listen(timeout=5)
            if not confirm or "yes" not in confirm.lower():
                voice.speak("Aborting login.")
                return

        # 4. Type Credentials
        voice.speak("Entering details.")
        appium_client.execute_action({"type": "input", "value": username})
        time.sleep(1)
        
        # Switch field? Usually 'tab' or tap password field. 
        # For now, simplistic input assuming focus or just append. 
        # Ideally we tap the password field. But we don't know where it is without coordinates?
        # The Action Agent is usually smarter. 
        # BUT `handle_auth_flow` is a special override.
        # Let's type password blindly or rely on standard "Enter" to Next.
        appium_client.execute_action({"type": "system", "command": "enter"}) # Move to next field
        time.sleep(1)
        
        appium_client.execute_action({"type": "input", "value": password})
        time.sleep(1)
            
        # 5. Submit
        voice.speak("Signing in.")
        # Try to tap "Sign In" or just hit Enter
        ocr_results = screen_state.get('ocr_results', [])
        submit_btn = screen_analyzer.find_text_coordinates("Sign In", ocr_results) or \
                     screen_analyzer.find_text_coordinates("Log In", ocr_results) or \
                     screen_analyzer.find_text_coordinates("Next", ocr_results)
                     
        if submit_btn:
            appium_client.execute_action({"type": "tap", "coordinates": submit_btn})
        else:
            appium_client.execute_action({"type": "system", "command": "enter"})

    def identify_page(self, ocr_results, initial=False):
        """Identifies the current page using Gemini"""
        visible_text = [item['text'] for item in ocr_results]
        prompt = f"Identify the screen based on text: {visible_text[:30]}. Return ONLY the page name (e.g. 'Settings', 'Home Screen')."
        
        try:
            page_name = gemini_client.generate_text(prompt).strip()
            if initial:
                voice.speak(f"You are on the {page_name}.")
            return page_name
        except:
            return "Unknown Page"

    def summarize_session(self, ocr_results=None, periodic=False):
        if not self.action_history: 
            return
        
        # Get visible text to identify page
        visible_text = []
        if ocr_results:
             visible_text = [item['text'] for item in ocr_results]
        elif hasattr(screen_analyzer, 'extract_text'):
             # Fallback: Quick scan if not provided
             res = screen_analyzer.extract_text("latest.png")
             visible_text = [item['text'] for item in res]
             
        prompt = f"""
        Actions Taken: {self.action_history}
        Visible Screen Text: {visible_text[:30]} 
        
        1. Summarize what was done in 1 sentence.
        2. Identify the current page/screen name.
        
        RESPONSE JSON:
        {{
            "summary": "We scrolled down twice.",
            "current_page": "Settings Page"
        }}
        """
        
        try:
            result = gemini_client.generate_json(prompt=prompt)
            summary = result.get('summary', 'Progress update.')
            page = result.get('current_page', 'unknown page')
            
            if periodic:
                voice.speak(f"Update: {summary}. Current page: {page}.")
            else:
                voice.speak(f"{summary} You are now on the {page}.")
        except:
            voice.speak("Task update.")

orchestrator = Orchestrator()