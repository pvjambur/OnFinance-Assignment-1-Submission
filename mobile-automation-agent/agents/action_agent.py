import logging
from typing import Dict, Any
from .base_agent import BaseAgent
from clients.google_genai_client import gemini_client

class ActionAgent(BaseAgent):
    def __init__(self):
        super().__init__('action_agent')

    def run(self, task_goal: str, screen_state: Dict[str, Any]) -> Dict[str, Any]:
        visible_text = [item['text'] for item in screen_state.get('ocr_results', [])]
        
        prompt = f"""
        Goal: {task_goal}
        Visible Text: {visible_text}
        
        Decide the next move.
        
        AVAILABLE ACTIONS:
        - "tap": Tap visible text.
        - "input": Type text.
        - "system": Use hardware keys ("home", "back", "recents", "notification", "volume_up").
        - "scroll": Scroll down.
        - "finish": Goal reached.
        
        RESPONSE FORMAT (JSON ONLY):
        {{
            "action": "tap" | "input" | "scroll" | "system" | "finish",
            "target_text": "text to tap",
            "value": "text to type OR system command (e.g. 'home', 'back')"
        }}
        """
        
        return gemini_client.generate_json(prompt=prompt) or {"action": "wait"}

action_agent = ActionAgent()