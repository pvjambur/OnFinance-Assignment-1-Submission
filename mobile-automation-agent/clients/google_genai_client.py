import google.genai as genai         # <--- CORRECT (New Library)
from google.genai import types
import logging
import json
from typing import Dict, Any, Optional
import base64
from config.settings import settings
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from google.api_core import exceptions

# Import Pillow here to ensure it's available
try:
    from PIL import Image
    import io
except ImportError:
    Image = None

logger = logging.getLogger(__name__)

class GoogleGenAIClient:
    def __init__(self):
        if not settings.GOOGLE_API_KEY:
            logger.warning("GOOGLE_API_KEY not set. Gemini client disabled.")
            self.client = None
            return

        try:
            # Initialize the client
            # For newer SDK, we access the API via the client
            self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
            self.model_name = "gemini-2.5-flash" 
            logger.info("✅ Google GenAI client initialized")
        except Exception as e:
            logger.error(f"❌ Failed to init GenAI client: {e}")
            self.client = None

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception) # Catch generic to handle API errors, ideally specific
    )
    def _generate(self, method_call: callable) -> Dict[str, Any]:
        try:
            response = method_call()
            # Handle cases where response might be None or blocked
            if not response or not response.text:
                logger.error("Empty response from Gemini")
                return {}
                
            # Parse JSON
            # Clean possible markdown code blocks
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            data = json.loads(text.strip())
            if not isinstance(data, dict):
                 logger.warning(f"GenAI returned non-dict JSON: {type(data)}")
                 return {"result": data} # Wrap it
            return data
            
        except json.JSONDecodeError:
            logger.error(f"Failed to decode JSON: {response.text}")
            return {}
        except Exception as e:
            if "RESOURCE_EXHAUSTED" in str(e):
                logger.warning("Rate limit hit, retrying...")
                raise e # Trigger tenacity retry
            logger.error(f"GenAI Generation Error: {e}")
            return {}

    def generate_json(self, prompt: str, system_prompt: str = "") -> Dict[str, Any]:
        """Generate structured JSON response"""
        if not self.client:
            logger.error("Client is not initialized.")
            return {}

        full_prompt = f"{system_prompt}\n\nUser Input: {prompt}\n\nOutput JSON:"
        
        def call_api():
             return self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
        return self._generate(call_api)

    def analyze_image(self, image_bytes: bytes, prompt: str) -> Dict[str, Any]:
        """Analyze image with vision model"""
        if not self.client:
            return {}
        
        if Image is None:
            logger.error("Pillow (PIL) is not installed. Cannot process images.")
            return {}
            
        try:
            image = Image.open(io.BytesIO(image_bytes))
            
            def call_api():
                return self.client.models.generate_content(
                    model=self.model_name,
                    contents=[prompt, image],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json"
                    )
                )

            return self._generate(call_api)
            
        except Exception as e:
            logger.error(f"GenAI Vision Error: {e}")
            return {}

gemini_client = GoogleGenAIClient()