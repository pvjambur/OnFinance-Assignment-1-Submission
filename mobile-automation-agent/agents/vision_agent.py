import logging
import base64
from typing import Dict, Any, List

from .base_agent import BaseAgent
from clients.google_genai_client import gemini_client
from core.screen_analyzer import screen_analyzer
from config.settings import settings

logger = logging.getLogger(__name__)

class VisionAgent(BaseAgent):
    def __init__(self):
        super().__init__('vision_agent')

    def run(self, screenshot_path: str) -> Dict[str, Any]:
        """
        Analyze screenshot using Hybrid Vision (Gemini + PaddleOCR).
        """
        logger.info(f"👀 Analyzing Screen: {screenshot_path}")

        # 1. OCR Extraction (Local, Fast, Precise)
        ocr_results = screen_analyzer.extract_text(screenshot_path)
        ocr_texts = [item['text'] for item in ocr_results]
        logger.debug(f"OCR Found {len(ocr_texts)} text elements")

        # 2. Vision Analysis (Cloud, Semantic)
        try:
            with open(screenshot_path, "rb") as img_file:
                img_bytes = img_file.read()
        except FileNotFoundError:
            logger.error(f"Screenshot not found: {screenshot_path}")
            return {"error": "file_not_found"}

        # Context Enrichment: Feed OCR results to GenAI to reduce hallucinations
        context_str = "\n".join([f"- {t}" for t in ocr_texts[:50]]) # Limit to top 50 to save tokens
        enriched_prompt = f"""
        {self.system_prompt}
        
        [GROUNDING DATA - OCR DETECTED TEXT]
        The following text was detected on screen by OCR. Use this to verify your findings:
        {context_str}
        
        [TASK]
        Analyze the image and return the JSON structure.
        """

        vision_result = gemini_client.analyze_image(
            image_bytes=img_bytes,
            prompt=enriched_prompt
        )

        if not vision_result:
            logger.warning("Gemini Vision returned empty. Falling back to raw OCR data.")
            return {
                "screen_type": "unknown",
                "elements": [], # TODO: Convert OCR boxes to UI elements if fallback needed
                "text_content": ocr_texts,
                "ocr_raw": ocr_results
            }

        # Attach OCR data for the Action Agent to use for coordinate lookup
        vision_result['ocr_enriched'] = ocr_results
        return vision_result

vision_agent = VisionAgent()
