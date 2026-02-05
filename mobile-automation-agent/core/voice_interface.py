import os
import time
import speech_recognition as sr
import pyttsx3
import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Callable
from config.settings import settings

logger = logging.getLogger(__name__)

class VoiceInterface:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.tts_engine = pyttsx3.init()
        self.setup_tts()
        self.executor = ThreadPoolExecutor(max_workers=1)

    def setup_tts(self):
        """Configure TTS voice and rate"""
        try:
            self.tts_engine.setProperty('rate', 175)
            voices = self.tts_engine.getProperty('voices')
            # Prefer female voice if available, usually clearer
            for voice in voices:
                if "female" in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
        except Exception as e:
            logger.warning(f"Failed to configure TTS: {e}")

    def speak(self, text: str):
        """Text to Speech (Blocking or Async would be better)"""
        logger.info(f"🤖 Speaking: {text}")
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            logger.error(f"TTS Error: {e}")

    def listen(self, timeout: int = 5) -> Optional[str]:
        """Listen for audio and convert to text"""
        logger.info("🎤 Listening...")
        
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout)
                
            # Hybrid STT: Try OpenAI Whisper API first (Quality), fallback to Google (Free/Unlimited)
            if settings.OPENAI_API_KEY:
                return self._transcribe_whisper(audio)
            else:
                return self._transcribe_google(audio)
                
        except sr.WaitTimeoutError:
            logger.info("Listening timed out (silence)")
            return None
        except Exception as e:
            logger.error(f"Listening error: {e}")
            return None

    def _transcribe_whisper(self, audio) -> str:
        """Use OpenAI Whisper API"""
        # Note: speech_recognition supports whisper if installed, or we use raw API
        # Here we use the simplified Google fallback if whisper lib isn't set up perfectly
        # But let's try to use the library's built-in whisper support if available
        # Try Whisper API if key exists, else Local
        if settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("sk-proj-"): # invalid key check
             try:
                text = self.recognizer.recognize_whisper_api(audio, api_key=settings.OPENAI_API_KEY)
                logger.info(f"🗣️ User (Whisper API): {text}")
                return text
             except Exception as e:
                logger.warning(f"Whisper API failed ({e}), trying local...")

        return self._transcribe_whisper_local(audio)

    def _transcribe_whisper_local(self, audio) -> str:
        """Use Local OpenAI Whisper (Free, Offline)"""
        try:
            # Requires: pip install openai-whisper
            text = self.recognizer.recognize_whisper(audio, model="base")
            logger.info(f"🗣️ User (Whisper Local): {text}")
            return text
        except AttributeError:
             logger.warning("Local Whisper not available/installed, falling back to Google")
             return self._transcribe_google(audio)
        except Exception as e:
            logger.error(f"Whisper Local Error: {e}")
            return self._transcribe_google(audio)

    def _transcribe_google(self, audio) -> str:
        """Use Google Speech Recognition (Free)"""
        try:
            text = self.recognizer.recognize_google(audio)
            logger.info(f"🗣️ User (Google): {text}")
            return text
        except sr.UnknownValueError:
            logger.info("Could not understand audio")
            return None
        except sr.RequestError as e:
            logger.error(f"Google SR Error: {e}")
            return None

voice = VoiceInterface()
