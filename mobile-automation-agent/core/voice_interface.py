import os
import speech_recognition as sr
import pyttsx3
import logging
import subprocess
from typing import Optional
from config.settings import settings

logger = logging.getLogger(__name__)

class VoiceInterface:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
        # --- SENSITIVITY TUNING ---
        self.recognizer.energy_threshold = 250
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.6
        self.recognizer.non_speaking_duration = 0.4

        # Only init pyttsx3 if NOT on Windows
        if os.name != 'nt':
            self.tts_engine = pyttsx3.init()
            self.setup_tts()
        else:
            self.tts_engine = None

    def setup_tts(self):
        if not self.tts_engine: return
        try:
            self.tts_engine.setProperty('rate', 175)
            voices = self.tts_engine.getProperty('voices')
            for voice in voices:
                if "female" in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
        except Exception as e:
            logger.error(f"TTS Setup Error: {e}")

    def speak(self, text: str):
        if not text: return
        logger.info(f"🤖 Speaking: {text}")
        
        # Windows PowerShell Method (Now BLOCKING)
        if os.name == 'nt':
            try:
                safe_text = text.replace("'", "''")
                # Using 'subprocess.run' makes Python WAIT until speaking finishes
                command = f"Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Rate = 0; $speak.Speak('{safe_text}')"
                subprocess.run(["powershell", "-Command", command], shell=True)
                return
            except Exception as e:
                logger.error(f"PowerShell TTS Error: {e}")
        
        # Fallback / Non-Windows (Already Blocking)
        if self.tts_engine:
            try:
                self.tts_engine.say(text)
                self.tts_engine.runAndWait()
            except Exception:
                pass

    def listen(self, timeout: int = 5) -> Optional[str]:
        if timeout > 2: logger.info("🎤 Listening...")
        
        try:
            with sr.Microphone() as source:
                if timeout > 2:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                
                try:
                    audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=8)
                except sr.WaitTimeoutError:
                    return None

            # 1. Whisper API
            if settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("sk-proj-"):
                try:
                    return self.recognizer.recognize_whisper_api(audio, api_key=settings.OPENAI_API_KEY)
                except: pass

            # 2. Local Whisper
            try:
                return self.recognizer.recognize_whisper(audio, model="base")
            except: pass

            # 3. Google Fallback
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