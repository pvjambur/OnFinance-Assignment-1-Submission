import logging
from paddleocr import PaddleOCR
from typing import List, Dict, Any
import cv2
import numpy as np

logger = logging.getLogger(__name__)

class ScreenAnalyzer:
    def __init__(self):
        # Initialize PaddleOCR (English, use_angle_cls=True)
        # Note: This loads model into memory.
        try:
            self.ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
            logger.info("✅ PaddleOCR initialized")
        except Exception as e:
            logger.error(f"Failed to init PaddleOCR: {e}")
            self.ocr = None

    def extract_text(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Extract text and bounding boxes from image.
        """
        if not self.ocr:
            return []

        try:
            result = self.ocr.ocr(image_path, cls=True)
            output = []
            if not result or result[0] is None:
                return []
                
            for line in result[0]:
                # line format: [[points], (text, confidence)]
                box = line[0]
                text, conf = line[1]
                
                # Calculate center point
                x_coords = [p[0] for p in box]
                y_coords = [p[1] for p in box]
                center_x = sum(x_coords) / 4
                center_y = sum(y_coords) / 4
                
                output.append({
                    "text": text,
                    "confidence": conf,
                    "box": box,
                    "center": (center_x, center_y)
                })
            return output
        except Exception as e:
            logger.error(f"OCR Error: {e}")
            return []

screen_analyzer = ScreenAnalyzer()
