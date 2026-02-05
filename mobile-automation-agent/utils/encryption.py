from cryptography.fernet import Fernet
from config.settings import settings
import base64
import logging

logger = logging.getLogger(__name__)

class EncryptionManager:
    def __init__(self):
        key = settings.ENCRYPTION_KEY
        if not key or key == "change-me-in-prod":
            # Generate a temp key if not set, but warn heavily
            logger.warning("⚠️ Using insecure temporary encryption key!")
            key = Fernet.generate_key().decode()
        
        # Ensure key is valid base64
        try:
            self.cipher = Fernet(key.encode(encoding='utf-8') if isinstance(key, str) else key)
        except Exception as e:
            logger.error(f"Encryption init failed: {e}")
            self.cipher = None

    def encrypt(self, data: str) -> str:
        if not self.cipher or not data:
            return data
        return self.cipher.encrypt(data.encode()).decode()

    def decrypt(self, token: str) -> str:
        if not self.cipher or not token:
            return token
        try:
            return self.cipher.decrypt(token.encode()).decode()
        except Exception:
            return token

encryptor = EncryptionManager()
