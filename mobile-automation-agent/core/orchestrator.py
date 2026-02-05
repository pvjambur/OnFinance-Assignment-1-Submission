import logging
import time
import asyncio
from typing import Dict, Any

from agents.intent_agent import intent_agent
from agents.vision_agent import vision_agent
from agents.action_agent import action_agent
from agents.auth_agent import auth_agent
from core.voice_interface import voice
from core.credential_manager import credential_manager
from config.settings import settings
from clients.appium_client import appium_client

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self):
        self.running = False
        self.current_user_id = "00000000-0000-0000-0000-000000000000" # Placeholder for demo

    def start(self):
        """Main Life Cycle"""
        logger.info("🚀 Mobile Agent Orchestrator Online")
        
        # Initialize Appium Driver
        # In a real scenario, we might want to do this based on user intent (e.g. "open app")
        # For now, we try to initialize at startup or mock if failed.
        if not appium_client.initialize_driver():
            logger.warning("⚠️ Appium Driver failed to initialize. Running in OBSERVATION-ONLY mode (or Mock).")
            # We continue; maybe the user just wants to chat or will connect later? 
            # Or we could Prompt the user?
            voice.speak("Warning. Mobile driver not connected.")
        
        voice.speak("I am ready. What would you like to do?")
        self.running = True
        
        while self.running:
            # 1. Listen
            user_command = voice.listen()
            if not user_command:
                continue

            if "stop" in user_command.lower() or "exit" in user_command.lower():
                voice.speak("Stopping.")
                break

            # 2. Parse Intent
            intent = intent_agent.run(user_command)
            if not isinstance(intent, dict):
                logger.error(f"Intent agent returned non-dict: {type(intent)}")
                voice.speak("I'm confused.")
                continue

            if intent.get('error'):
                voice.speak("I didn't catch that.")
                continue

            # 3. Execute Task
            self.execute_task_loop(intent)
        
        # Cleanup
        appium_client.quit()

    def execute_task_loop(self, intent: Dict[str, Any]):
        """Execution Loop for a single task"""
        app_name = intent.get('app', {}).get('name', 'app')
        voice.speak(f"Okay, opening {app_name}")
        
        step = 0
        max_steps = 10
        
        while step < max_steps:
            # A. Capture State
            # Capture real screenshot
            screenshot_path = appium_client.capture_screenshot("latest_screenshot.png")
            
            if not screenshot_path or not os.path.exists(screenshot_path):
                 # Failover for testing without device
                 if step == 0:
                     logger.warning("No screenshot captured. Is device connected?")
                     # voice.speak("I can't see the screen.")
                     # break or continue to try mock?
                     # For now, we continue to let VisionAgent handle "file not found" or "black screen"
                 pass
            
            # B. Analyze Screen
            vision_result = vision_agent.run("latest_screenshot.png")
            
            # C. Check Security/Auth
            auth_check = auth_agent.run(vision_result)
            if auth_check.get('is_auth_screen'):
                self.handle_auth(vision_result)
                continue # Re-evaluate after auth handling

            # D. Plan Action
            action_plan = action_agent.run(
                task_goal=intent.get('query', 'navigate'),
                screen_state=vision_result
            )
            
            # Checks to prevent crash if action_plan is None or not a dict
            if not isinstance(action_plan, dict):
                 logger.error(f"Action planning returned non-dict: {action_plan}")
                 step += 1
                 continue

            # E. Execute Action
            # Execute real action
            action_data = action_plan.get('action')
            if action_data:
                appium_client.execute_action(action_data)
                self.perform_action_log(action_data)
            
            step += 1
            time.sleep(2)

    def handle_auth(self, screen_state: Dict[str, Any]):
        """Handle Login Flow"""
        voice.speak("Login screen detected.")
        # Logic to fetch credentials and auto-fill
        # creds = credential_manager.get_credential(...)
        # if creds: fill_form(creds)
        pass

    def perform_action_log(self, action: Dict[str, Any]):
        """Log action for debug"""
        logger.info(f"Acting: {action}")

orchestrator = Orchestrator()
