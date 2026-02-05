from .base_agent import BaseAgent
from clients.gemini_client import gemini_client
from core.screen_analyzer import screen_analyzer
from typing import Dict, Any
import base64

class VisionAgent(BaseAgent):
    def __init__(self):
        super().__init__('vision_agent')

    def run(self, screenshot_path: str) -> Dict[str, Any]:
        """Analyze screenshot"""
        
        # 1. OCR (Fast, Local)
        ocr_results = screen_analyzer.extract_text(screenshot_path)
        ocr_text = [item['text'] for item in ocr_results]
        
        # 2. Vision Model (Smart, Cloud)
        with open(screenshot_path, "rb") as img_file:
            img_bytes = img_file.read()
            
        # Context enrichment for Gemini
        context = f"Detected Text (OCR): {', '.join(ocr_text)}"
        full_system_prompt = f"{self.system_prompt}\n\nContext:\n{context}"
        
        vision_result = gemini_client.analyze_image(img_bytes, full_system_prompt)
        
        # Merge results (Simple merge for MVP: Attach OCR raw data to result)
        if vision_result:
            vision_result['ocr_data'] = ocr_results
            
        return vision_result
