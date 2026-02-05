from .base_agent import BaseAgent
from typing import Dict, Any

class TypingAgent(BaseAgent):
    def __init__(self):
        super().__init__('typing_agent')

    def run(self, goal: str, screen_state: Dict[str, Any]) -> Dict[str, Any]:
        ocr_results = screen_state.get('ocr_results', [])
        # Simplified context for typing
        visible_text = [item['text'] for item in ocr_results]
        
        prompt = f"""
        Goal: {goal}
        Visible Text: {visible_text[:50]}...
        """
        return self.generate_response(prompt)

typing_agent = TypingAgent()
