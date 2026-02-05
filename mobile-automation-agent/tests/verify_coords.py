
import logging
from typing import Dict, Any

# Mocking logger to see output
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock ActionAgent class
class MockActionAgent:
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

        print(f"📍 Attempting to resolve coordinates for: '{target_text}'")
        
        # 1. Exact Match
        for item in ocr_data:
            if item['text'].lower() == target_text.lower():
                action['coordinates'] = item['center']
                print(f"✅ Found exact match: {target_text} at {item['center']}")
                return action_plan

        # 2. Partial Match
        for item in ocr_data:
            if target_text.lower() in item['text'].lower() or item['text'].lower() in target_text.lower():
                 action['coordinates'] = item['center']
                 print(f"✅ Found partial match: '{target_text}' ~ '{item['text']}' at {item['center']}")
                 return action_plan

        print(f"❌ Could not resolve coordinates for: {target_text}")
        return action_plan

def test_resolution():
    agent = MockActionAgent()
    
    # Mock Data
    screen_state = {
        "ocr_enriched": [
            {"text": "Settings", "center": (500, 1000)},
            {"text": "Chrome", "center": (200, 500)},
            {"text": "Play Store", "center": (800, 500)}
        ]
    }
    
    # Test 1: Exact Match
    plan1 = {"action": {"type": "tap", "target": "Settings"}}
    res1 = agent.resolve_coordinates(plan1, screen_state)
    assert res1['action']['coordinates'] == (500, 1000)
    
    # Test 2: Partial Match
    plan2 = {"action": {"type": "tap", "target": "Chrome Browser"}}
    res2 = agent.resolve_coordinates(plan2, screen_state)
    assert res2['action']['coordinates'] == (200, 500)
    
    # Test 3: No Match
    plan3 = {"action": {"type": "tap", "target": "Twitter"}}
    res3 = agent.resolve_coordinates(plan3, screen_state)
    assert 'coordinates' not in res3['action']
    
    print("\n🎉 All tests passed!")

if __name__ == "__main__":
    test_resolution()
