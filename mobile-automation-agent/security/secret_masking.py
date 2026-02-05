import re
from typing import str

PATTERNS = [
    r'(password|pin|secret|key|token)["\']?\s*[:=]\s*["\']?([^"\' \n]+)',
    r'(\d{4}-\d{4}-\d{4}-\d{4})',  # Credit Card
    r'\b[\w\.-]+@[\w\.-]+\.\w+\b'  # Email (optional masking)
]

def mask_secrets(text: str) -> str:
    """Mask sensitive information in text."""
    if not isinstance(text, str):
        return text
        
    masked = text
    for pattern in PATTERNS:
        masked = re.sub(pattern, r'\1: *****', masked, flags=re.IGNORECASE)
    return masked

class SecretFilter(logging.Filter):
    def filter(self, record):
        if isinstance(record.msg, str):
            record.msg = mask_secrets(record.msg)
        return True
