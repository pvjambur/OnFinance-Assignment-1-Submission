import logging
from typing import Dict, Any

from .base_agent import BaseAgent
from clients.google_genai_client import gemini_client

logger = logging.getLogger(__name__)

class AuthAgent(BaseAgent):
    def __init__(self):
        super().__init__('auth_agent')
        # Fast keywords to trigger Auth Mode
        self.auth_keywords = ["sign in", "log in", "username", "password", "email address", "forgot password"]

    def is_login_screen(self, screen_state: Dict[str, Any]) -> bool:
        """
        Fast check: Does the screen look like a login page?
        """
        visible_text = [item['text'].lower() for item in screen_state.get('ocr_results', [])]
        
        # 1. Fast Keyword Match (Instant)
        matches = [word for word in self.auth_keywords if any(word in t for t in visible_text)]
        
        # If we see "Password" AND ("Sign In" or "Log In"), it's definitely a login screen
        has_password = any("password" in t for t in visible_text)
        has_signin = any("sign in" in t for t in visible_text) or any("log in" in t for t in visible_text)
        
        if has_password and has_signin:
            logger.info("🔒 Auth Keyword Match detected")
            return True
            
        return False

    def run(self, *args, **kwargs):
        # Legacy method support if needed
        pass

auth_agent = AuthAgent()
