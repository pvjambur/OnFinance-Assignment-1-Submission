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
        
        # 2. Heuristic Check
        # If we see "Sign In"/"Log In" AND tokens like "Password", "Email", "Username", or "Next"
        has_auth_action = any(k in t for t in visible_text for k in ["sign in", "log in", "next", "continue"])
        has_field = any(k in t for t in visible_text for k in ["password", "email", "username", "phone", "verify"])
        
        if has_auth_action and has_field:
            logger.info("🔒 Auth Keyword Match detected")
            return True
            
        # 3. Super permissive check for "Sign in" title
        if any(t == "sign in" or t == "log in" for t in visible_text):
             return True
             
        return False

    def run(self, *args, **kwargs):
        # Legacy method support if needed
        pass

auth_agent = AuthAgent()
