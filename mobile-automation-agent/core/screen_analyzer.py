import logging
import os
import pytesseract
from PIL import Image, ImageOps
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ScreenAnalyzer:
    def __init__(self):
        # Update this list if Tesseract is installed elsewhere
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Users\jambu\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
        ]
        
        found_path = None
        for path in possible_paths:
            if os.path.exists(path):
                found_path = path
                break
        
        if found_path:
            pytesseract.pytesseract.tesseract_cmd = found_path
            logger.info(f"✅ Tesseract found at: {found_path}")
            self.ready = True
        else:
            self.ready = False
            logger.warning("❌ Tesseract not found. OCR will not work.")

    def extract_text(self, image_path: str) -> List[Dict[str, Any]]:
        if not self.ready or not os.path.exists(image_path):
            return []

        try:
            img = Image.open(image_path)
            # Optimization: Resize huge screenshots to speed up processing
            img.thumbnail((1080, 1920)) 
            
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            output = []
            
            for i in range(len(data['text'])):
                conf = int(data['conf'][i])
                text = data['text'][i].strip()
                
                if conf > 40 and len(text) > 1:
                    x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                    center_x, center_y = x + w//2, y + h//2
                    
                    output.append({
                        "text": text,
                        "center": (center_x, center_y)
                    })
            return output
        except Exception as e:
            logger.error(f"OCR Error: {e}")
            return []

    def find_text_coordinates(self, target_text: str, ocr_results: List[Dict]) -> Optional[tuple]:
        """
        Instantly find coordinates for text (Case-insensitive fuzzy match)
        """
        target = target_text.lower()
        
        # 1. Exact Match
        for item in ocr_results:
            if item['text'].lower() == target:
                return item['center']
                
        # 2. Partial Match (e.g. "Setting" in "Settings")
        for item in ocr_results:
            if target in item['text'].lower() or item['text'].lower() in target:
                return item['center']
        
        return None

screen_analyzer = ScreenAnalyzer()
