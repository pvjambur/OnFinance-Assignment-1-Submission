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
        
        RESPONSE FORMAT:
        {{
            "action": {{
                "type": "tap" | "input" | "scroll" | "wait" | "finish",
                "target": "element_description_or_id",
                "value": "text_to_type_if_input"
            }}
        }}
        """

        response = gemini_client.generate_json(
            prompt=prompt,
            system_prompt=self.system_prompt
        )

        if not response:
            logger.error("Action planning failed")
            return {"action": {"type": "wait", "reason": "planning_failed"}}

        action = response.get('action', {})
        
        if isinstance(action, dict):
            logger.info(f"👉 Decided: {action.get('type')} -> {action.get('target', 'none')}")
        else:
            logger.warning(f"👉 Decided (Non-Standard): {action}")
            
        return response

    def resolve_coordinates(self, action_plan: Dict[str, Any], screen_state: Dict[str, Any]):
        """
        Injects coordinates into the action plan if the target is a text label.
        Matches action_plan['action']['target'] against screen_state['ocr_enriched'].
        """
        if not isinstance(action_plan, dict) or 'action' not in action_plan:
            return action_plan

        action = action_plan['action']
        target_text = action.get('target')
        
        # Only resolve if it's a tap/click and no coordinates exist
        if action.get('type') not in ['tap', 'click'] or action.get('coordinates'):
            return action_plan

        ocr_data = screen_state.get('ocr_enriched', [])
        if not ocr_data or not target_text:
            return action_plan

        logger.info(f"📍 Attempting to resolve coordinates for: '{target_text}'")
        
        # 1. Exact Match
        for item in ocr_data:
            if item['text'].lower() == target_text.lower():
                action['coordinates'] = item['center']
                logger.info(f"✅ Found exact match: {target_text} at {item['center']}")
                return action_plan

        # 2. Partial Match
        for item in ocr_data:
            if target_text.lower() in item['text'].lower() or item['text'].lower() in target_text.lower():
                 action['coordinates'] = item['center']
                 logger.info(f"✅ Found partial match: '{target_text}' ~ '{item['text']}' at {item['center']}")
                 return action_plan

        logger.warning(f"❌ Could not resolve coordinates for: {target_text}")
        return action_plan

action_agent = ActionAgent()
