import pytest
import sys
from unittest.mock import MagicMock, patch

# Mock dependencies before imports if they rely on hardware/network
sys.modules['paddleocr'] = MagicMock()
sys.modules['pyttsx3'] = MagicMock()
sys.modules['speech_recognition'] = MagicMock()

from agents.intent_agent import IntentAgent

@pytest.fixture
def mock_gemini():
    with patch('clients.google_genai_client.gemini_client.generate_json') as mock:
        yield mock

def test_intent_parsing(mock_gemini):
    # Setup
    agent = IntentAgent()
    mock_gemini.return_value = {"intent": "open_app", "app": {"name": "YouTube"}}
    
    # Execute
    result = agent.run("Open YouTube")
    
    # Verify
    assert result['intent'] == "open_app"
    assert result['app']['name'] == "YouTube"
