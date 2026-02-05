import logging
from typing import Optional, Dict
from clients.supabase_client import supabase_client
from utils.encryption import encryptor
from models.credential import Credential

logger = logging.getLogger(__name__)

class CredentialManager:
    def __init__(self):
        self.supabase = supabase_client

    def get_credential(self, user_id: str, app_name: str) -> Optional[Dict[str, str]]:
        """
        Retrieve and decrypt credentials for a specific app.
        """
        if not self.supabase:
            return None

        try:
            # 1. Fetch from DB
            response = self.supabase.table("credentials")\
                .select("*")\
                .eq("user_id", user_id)\
                .eq("app_name", app_name)\
                .execute()
            
            if not response.data:
                return None
                
            record = response.data[0]
            
            # 2. Decrypt locally (Application Layer Encryption)
            email = encryptor.decrypt(record.get('email_encrypted'))
            password = encryptor.decrypt(record.get('password_encrypted'))
            
            return {
                "email": email,
                "password": password,
                "metadata": record.get('metadata')
            }
        except Exception as e:
            logger.error(f"Failed to retrieve credentials: {e}")
            return None

    def store_credential(self, user_id: str, app_name: str, email: str, password: str):
        """
        Encrypt and store new credentials.
        """
        if not self.supabase:
            return False

        try:
            # Encrypt locally before sending
            email_enc = encryptor.encrypt(email)
            pass_enc = encryptor.encrypt(password)
            
            data = {
                "user_id": user_id,
                "app_name": app_name,
                "email_encrypted": email_enc,
                "password_encrypted": pass_enc
            }
            
            self.supabase.table("credentials").upsert(data).execute()
            logger.info(f"Credential stored for {app_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to store credential: {e}")
            return False

credential_manager = CredentialManager()
