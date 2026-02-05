from .base_agent import BaseAgent
from clients.gemini_client import gemini_client
from typing import Dict, Any

class AuthAgent(BaseAgent):
    def __init__(self):
        super().__init__('auth_agent')

    def run(self, screen_state: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze authentication needs"""
        
        screen_dump = str(screen_state)
        return gemini_client.generate_json(screen_dump, system_prompt=self.system_prompt)
