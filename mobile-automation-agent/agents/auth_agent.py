import logging
from typing import Dict, Any

from .base_agent import BaseAgent
from clients.google_genai_client import gemini_client

logger = logging.getLogger(__name__)

class AuthAgent(BaseAgent):
    def __init__(self):
        super().__init__('auth_agent')

    def run(self, screen_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze if the current screen is a login screen and what credentials are needed.
        """
        if screen_state.get('screen_type') != 'login':
            return {"is_auth_screen": False}

        logger.info("🔒 Analyzing Auth Screen")

        prompt = f"""
        Screen Elements: {screen_state.get('elements')}
        Text Content: {screen_state.get('text_content')}
        
        Identify input fields and required credentials.
        """

        response = gemini_client.generate_json(
            prompt=prompt,
            system_prompt=self.system_prompt
        )
        
        if response.get('is_auth_screen'):
            logger.info(f"🔑 Auth Required: {response.get('auth_type')}")
        
        return response

auth_agent = AuthAgent()
