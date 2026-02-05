import pytest
from unittest.mock import MagicMock, patch
import sys

# Mock hardware libs
sys.modules['pyttsx3'] = MagicMock()
sys.modules['speech_recognition'] = MagicMock()

from core.voice_interface import VoiceInterface

def test_voice_speak():
    voice = VoiceInterface()
    voice.tts_engine = MagicMock()
    
    voice.speak("Hello")
    
    voice.tts_engine.say.assert_called_with("Hello")
    voice.tts_engine.runAndWait.assert_called_once()
