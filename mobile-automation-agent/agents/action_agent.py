from .base_agent import BaseAgent
from clients.gemini_client import gemini_client
from typing import Dict, Any, List

class ActionAgent(BaseAgent):
    def __init__(self):
        super().__init__('action_agent')

    def run(self, task_goal: str, screen_state: Dict[str, Any]) -> Dict[str, Any]:
        """Decide next action"""
        
        screen_desc = {
            "type": screen_state.get('screen_type', 'unknown'),
            "elements": [e['label'] for e in screen_state.get('elements', []) if e.get('is_visible')]
        }
        
        prompt = f"""
        Current Task: {task_goal}
        Screen State: {screen_desc}
        """
        
        return gemini_client.generate_json(prompt, system_prompt=self.system_prompt)
