from .base_agent import BaseAgent
from clients.gemini_client import gemini_client
from typing import Dict, Any

class IntentAgent(BaseAgent):
    def __init__(self):
        super().__init__('intent_agent')

    def run(self, user_command: str) -> Dict[str, Any]:
        """Parse user command"""
        if not user_command:
            return {}

        prompt = f"User Command: {user_command}"
        return gemini_client.generate_json(prompt, system_prompt=self.system_prompt)
