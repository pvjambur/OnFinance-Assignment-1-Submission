import logging
import time
import os
from typing import Dict, Any

from agents.intent_agent import intent_agent
from agents.vision_agent import vision_agent
from agents.action_agent import action_agent
from agents.auth_agent import auth_agent
from core.voice_interface import voice
from config.settings import settings
from clients.appium_client import appium_client

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self):
        self.running = False

    def start(self):
        """Main Life Cycle"""
        logger.info("🚀 Mobile Agent Orchestrator Online")
        
        # Try to initialize driver
        driver_ready = appium_client.initialize_driver()
        if not driver_ready:
            logger.warning("⚠️ Running in OBSERVATION/MOCK Mode (No Driver)")
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
            
            # Safety Check: Did intent_agent return a Dictionary?
            if not isinstance(intent, dict):
                logger.error(f"Intent Error: Expected dict, got {type(intent)}")
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
        voice.speak("Processing.")
        
        step = 0
        max_steps = 20 # Increased from 10
        history = []

        while step < max_steps:
            logger.info(f"--- Step {step + 1}/{max_steps} ---")
            
            # A. Capture State
            screenshot_path = appium_client.capture_screenshot("latest_screenshot.png")
            if not screenshot_path:
                 logger.error("❌ No screenshot. Is Emulator running?")
                 break
            
            # B. Analyze Screen
            vision_result = vision_agent.run("latest_screenshot.png")
            
            # C. Plan Action
            action_plan = action_agent.run(
                task_goal=intent.get('query', 'navigate'),
                screen_state=vision_result,
                previous_actions=history[-3:] # Pass recent history
            )
            
            if not isinstance(action_plan, dict):
                 logger.error(f"Invalid plan format: {action_plan}")
                 step += 1
                 continue

            # D. RESOLVE COORDINATES (Fix for "Tap requested but no coordinates")
            action_plan = action_agent.resolve_coordinates(action_plan, vision_result)

            # E. Execute
            appium_client.execute_action(action_plan)
            
            # Track history for summary
            if 'action' in action_plan:
                history.append(f"Step {step+1}: {action_plan['action'].get('type')} -> {action_plan['action'].get('target')}")

            # Check finish
            if action_plan.get('action') == 'finish' or action_plan.get('type') == 'finish':
                voice.speak("Done.")
                break
            
            if isinstance(action_plan.get('action'), dict) and action_plan['action'].get('type') == 'finish':
                voice.speak("Done.")
                break
            
            step += 1
            # REMOVED: time.sleep(2) for speed optimization. 
            # Appium actions usually take enough time that we don't need extra sleep.
        
        # End of Loop Summary
        self.generate_summary(intent.get('query'), history)

    def generate_summary(self, goal, history):
        """Generate and speak a summary of the session"""
        if not history:
            return

        summary_prompt = f"""
        Goal: {goal}
        Actions Taken:
        {history}
        
        Summarize what was achieved in 1 short sentence.
        """
        try:
            logger.info("📝 Generating Summary...")
            # Using gemini_client directly for a quick summary
            from clients.google_genai_client import gemini_client
            summary = gemini_client.generate_text(summary_prompt)
            logger.info(f"📝 Summary: {summary}")
            voice.speak(f"Summary: {summary}")
        except Exception as e:
            logger.error(f"Failed to generate summary: {e}")

    def handle_auth(self, screen_state: Dict[str, Any]):
        voice.speak("Login screen detected.")
        pass

orchestrator = Orchestrator()