import os
import speech_recognition as sr
import pyttsx3
import logging
from typing import Optional
from config.settings import settings

logger = logging.getLogger(__name__)

class VoiceInterface:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
        # --- SENSITIVITY TUNING ---
        self.recognizer.energy_threshold = 250  # Lowered to pick up softer voices
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.6   # Wait only 0.6s after speech ends (Faster)
        self.recognizer.non_speaking_duration = 0.4
        # --------------------------

        self.tts_engine = pyttsx3.init()
        self.setup_tts()

    def setup_tts(self):
        try:
            self.tts_engine.setProperty('rate', 175)
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if "female" in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
        except: pass

    def speak(self, text: str):
        if not text: return
        logger.info(f"🤖 Speaking: {text}")
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except: pass

    def listen(self, timeout: int = 5) -> Optional[str]:
        """Robust Listening"""
        if timeout > 2: logger.info("🎤 Listening...")
        
        try:
            with sr.Microphone() as source:
                # Fast noise check (0.3s) prevents "hanging"
                if timeout > 2:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                
                try:
                    # phrase_time_limit=8 ensures it stops listening if background noise is constant
                    audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=8)
                except sr.WaitTimeoutError:
                    return None

            # 1. Try Whisper API
            if settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("sk-proj-"):
                try:
                    return self.recognizer.recognize_whisper_api(audio, api_key=settings.OPENAI_API_KEY)
                except: pass

            # 2. Try Local Whisper (Best for free quality)
            try:
                # pip install openai-whisper
                return self.recognizer.recognize_whisper(audio, model="base")
            except: 
                pass

            # 3. Fallback to Google (Standard)
            return self._transcribe_google(audio)

        except Exception as e:
            logger.error(f"Mic Error: {e}")
            return None

    def _transcribe_google(self, audio) -> str:
        try:
            text = self.recognizer.recognize_google(audio)
            logger.info(f"🗣️ User (Google): {text}")
            return text
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            return ""

voice = VoiceInterface()