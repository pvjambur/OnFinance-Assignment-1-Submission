import logging
from typing import Dict, Any, List
from .base_agent import BaseAgent
from clients.google_genai_client import gemini_client

class ActionAgent(BaseAgent):
    def __init__(self):
        super().__init__('action_agent')
    
    def run(self, task_goal: str, screen_state: Dict[str, Any]) -> Dict[str, Any]:
        ocr_results = screen_state.get('ocr_results', [])
        
        # Build detailed visible elements with coordinates
        visible_elements = []
        for item in ocr_results:
            visible_elements.append({
                'text': item['text'],
                'x': item.get('x', 0),
                'y': item.get('y', 0)
            })
        
        prompt = f"""
        Goal: {task_goal}
        Visible Elements (with coordinates): {visible_elements}
        
        RULES:
        1. If goal is achieved, return "action": "finish".
        2. DO NOT go "home" unless explicitly asked.
        3. To type text, FIRST tap the input field, THEN type.
        4. Use EXACT text from visible elements.
        5. Provide coordinates when tapping.
        
        AVAILABLE ACTIONS:
        - "tap": Tap element at coordinates
        - "input": Type text (use AFTER tapping input field)
        - "system": Use keys ("home", "back", "recents", "volume_up")
        - "scroll": Scroll down
        - "finish": Goal reached
        
        RESPONSE FORMAT (JSON ONLY):
        {{
            "action": "tap" | "input" | "scroll" | "system" | "finish",
            "target_text": "exact text to tap (for tap action)",
            "coordinates": {{"x": 100, "y": 200}},
            "value": "text to type (for input) OR system command"
        }}
        
        IMPORTANT: When you need to type something:
        Step 1: Return tap action with input field coordinates
        Step 2: On next call, return input action with the text
        """
        
        response = gemini_client.generate_json(prompt=prompt)
        
        if not response:
            return {"action": "wait"}
            
        # Ensure coordinates are included for tap actions
        if response.get('action') == 'tap' and 'coordinates' not in response:
            target = response.get('target_text', '')
            # Find coordinates from OCR results
            for item in ocr_results:
                if target.lower() in item['text'].lower():
                    response['coordinates'] = {
                        'x': item.get('x', 0),
                        'y': item.get('y', 0)
                    }
                    break
        
        return response

action_agent = ActionAgent()