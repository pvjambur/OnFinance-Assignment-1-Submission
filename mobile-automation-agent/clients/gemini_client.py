import google.generativeai as genai
import logging
import json
from typing import Dict, Any, Optional
from config.settings import settings

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        if not settings.GOOGLE_API_KEY:
            logger.warning("GOOGLE_API_KEY not set. Gemini client disabled.")
            self.model = None
            return

        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        self.vision_model = genai.GenerativeModel('gemini-1.5-flash') # Flash supports vision too

    def generate_json(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        """Generate structured JSON response"""
        if not self.model:
            return {}

        full_prompt = f"{system_prompt}\n\nUser Input: {prompt}\n\nOutput JSON:"
        
        try:
            response = self.model.generate_content(
                full_prompt,
                generation_config={'response_mime_type': 'application/json'}
            )
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Gemini Generation Error: {e}")
            return {}

    def analyze_image(self, image_bytes: bytes, prompt: str) -> Dict[str, Any]:
        """Analyze image with vision model"""
        if not self.vision_model:
            return {}
            
        try:
            img_part = {
                "mime_type": "image/png",
                "data": image_bytes
            }
            
            response = self.vision_model.generate_content(
                [prompt, img_part],
                generation_config={'response_mime_type': 'application/json'}
            )
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Gemini Vision Error: {e}")
            return {}

gemini_client = GeminiClient()
