import logging
import json
from typing import Dict, Any, Optional

from .base_agent import BaseAgent
from clients.google_genai_client import gemini_client
from models.task import TaskCreate, TaskStatus
from config.settings import settings

logger = logging.getLogger(__name__)

class IntentAgent(BaseAgent):
    def __init__(self):
        super().__init__('intent_agent')

    def run(self, user_command: str) -> Dict[str, Any]:
        """
        Parse user command into structured intent.
        Returns a dict matching the output_schema in intent_agent.yaml.
        """
        if not user_command:
            logger.warning("IntentAgent received empty command")
            return {}

        logger.info(f"🧠 Parsing Intent: {user_command}")
        
        # Construct Prompt
        prompt = f"User Command: {user_command}"
        
        # --- FIX IS HERE ---
        # Check 'client' instead of 'model'
        if not gemini_client.client: 
            logger.warning("⚠️ Gemini disabled. Using Mock Intent.")
            # Simple keyword matching for demo
            if "browser" in user_command.lower():
                return {"intent": "browse", "app": {"name": "Chrome"}, "query": user_command}
            elif "email" in user_command.lower():
                 return {"intent": "email", "app": {"name": "Gmail"}, "query": user_command}
            else:
                 return {"intent": "unknown", "error": "No API Key & No Keyword Match"}

        # Call Gemini
        response = gemini_client.generate_json(
            prompt=prompt,
            system_prompt=self.system_prompt
        )

        if not response:
            logger.error("Failed to parse intent")
            return {"intent": "unknown", "error": "AI generation failed"}

        logger.info(f"✅ Intent: {response.get('intent')} | App: {response.get('app', {}).get('name')}")
        return response

intent_agent = IntentAgent()