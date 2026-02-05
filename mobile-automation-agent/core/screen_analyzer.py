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
            img = Image.open(image_path)
            # REMOVED: img.thumbnail((1080, 1920)) - Caused coordinate mismatch with AppiumClient
            # We must OCR the original size so coordinates match the screenshot dimensions.
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
        Instantly find coordinates with smart matching (Case-insensitive, Punctuation-agnostic)
        """
        import string
        
        def clean(s): 
            return s.lower().translate(str.maketrans('', '', string.punctuation)).strip()
            
        target_clean = clean(target_text)
        if not target_clean: 
            return None # Empty target
        
        # 1. Exact "Clean Mode" Match
        for item in ocr_results:
            if clean(item['text']) == target_clean:
                return item['center']
                
        # 2. Substring Match (e.g., target="Settings" matches "Settings ->")
        for item in ocr_results:
            item_clean = clean(item['text'])
            if target_clean in item_clean or item_clean in target_clean:
                # Avoid matching very short noise (e.g. "I" matching in "Info")
                if len(item_clean) < 3 and item_clean != target_clean:
                    continue
                return item['center']
                
        # 3. Word Split Match (e.g. target="Google Play" matches "Play")
        target_words = target_clean.split()
        if len(target_words) > 1:
            for word in target_words:
                if len(word) < 4: continue # Skip small words
                for item in ocr_results:
                    if word in clean(item['text']):
                        return item['center']
        
        return None

screen_analyzer = ScreenAnalyzer()
