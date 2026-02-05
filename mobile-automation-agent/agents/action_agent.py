import logging
from typing import Dict, Any
from .base_agent import BaseAgent
from clients.google_genai_client import gemini_client

logger = logging.getLogger(__name__)

class ActionAgent(BaseAgent):
    def __init__(self):
        super().__init__('action_agent')

    def run(self, task_goal: str, screen_state: Dict[str, Any]) -> Dict[str, Any]:
        
        # We only send visible text to the LLM to save tokens and time
        visible_text = [item['text'] for item in screen_state.get('ocr_results', [])]
        
        prompt = f"""
        Goal: {task_goal}
        Visible Text on Screen: {visible_text}
        
        Decide the next move. If you want to tap something, just give me the text label.
        
        RESPONSE FORMAT (JSON ONLY):
        {{
            "action": "tap" | "input" | "scroll" | "finish",
            "target_text": "Exact text from screen to tap (e.g. 'Settings')",
            "value": "text to type (if input)"
        }}
        """

        response = gemini_client.generate_json(prompt=prompt)
        
        if not response:
            return {"action": "wait"}
            
        return response

action_agent = ActionAgent()
