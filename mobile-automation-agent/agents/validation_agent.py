from .base_agent import BaseAgent
from typing import Dict, Any

class ValidationAgent(BaseAgent):
    def __init__(self):
        super().__init__('validation_agent')

    def run(self, goal: str, screen_state: Dict[str, Any]) -> Dict[str, Any]:
        ocr_results = screen_state.get('ocr_results', [])
        visible_text = [item['text'] for item in ocr_results]
        
        prompt = f"""
        Goal: {goal}
        Visible Text: {visible_text}
        """
        return self.generate_response(prompt)

validation_agent = ValidationAgent()
