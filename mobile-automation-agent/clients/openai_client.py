import logging
from openai import OpenAI
from config.settings import settings

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self):
        self.client = None
        if settings.OPENAI_API_KEY:
            try:
                self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
                logger.info("✅ OpenAI client initialized")
            except Exception as e:
                logger.error(f"❌ OpenAI init failed: {e}")
        else:
            logger.info("ℹ️ OpenAI Key missing. Skipping.")

    def transcribe_audio(self, audio_file_path: str) -> str:
        """Transcribe audio using Whisper"""
        if not self.client:
            return None
            
        try:
            with open(audio_file_path, "rb") as audio:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio
                )
            return transcript.text
        except Exception as e:
            logger.error(f"Whisper Error: {e}")
            return None

openai_client = OpenAIClient()
