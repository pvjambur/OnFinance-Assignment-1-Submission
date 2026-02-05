import logging
from typing import Dict, Any

from .base_agent import BaseAgent
from clients.google_genai_client import gemini_client
from config.settings import settings

logger = logging.getLogger(__name__)

class ActionAgent(BaseAgent):
    def __init__(self):
        super().__init__('action_agent')

    def run(self, task_goal: str, screen_state: Dict[str, Any], previous_actions: list = []) -> Dict[str, Any]:
        """
        Decide the next action based on Goal + Screen.
        """
        logger.info(f"⚡ Planning Action for: {task_goal}")

        # simplify screen state for prompt to save tokens
        screen_summary = {
            "type": screen_state.get('screen_type', 'unknown'),
            "visible_text": screen_state.get('text_content', [])[:20],
            "interactive_elements": [
                f"{e.get('label')} ({e.get('type')})" 
                for e in screen_state.get('elements', []) 
                if e.get('is_visible')
            ]
        }

        prompt = f"""
        Current Goal: {task_goal}
        
        Screen State:
        {screen_summary}
        
        Previous Actions:
        {previous_actions}
        
        Determine the next single action.
        """

        response = gemini_client.generate_json(
            prompt=prompt,
            system_prompt=self.system_prompt
        )

        if not response:
            logger.error("Action planning failed")
            return {"action": {"type": "wait", "reason": "planning_failed"}}

        action = response.get('action', {})
        logger.info(f"👉 Decided: {action.get('type')} -> {action.get('target', 'none')}")
        return response

action_agent = ActionAgent()
