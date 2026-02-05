from .base_agent import BaseAgent
from typing import Dict, Any

class SettingsAgent(BaseAgent):
    def __init__(self):
        super().__init__('settings_agent')

    def run(self, goal: str, screen_state: Dict[str, Any]) -> Dict[str, Any]:
        prompt = f"Goal: {goal}"
        return self.generate_response(prompt)

settings_agent = SettingsAgent()
