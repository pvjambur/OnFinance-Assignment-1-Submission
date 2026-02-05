import logging
from supabase import create_client, Client
from config.settings import settings

logger = logging.getLogger(__name__)

class SupabaseManager:
    _instance = None

    def __init__(self):
        self.client: Client = None
        if settings.ENABLE_SUPABASE:
            self.connect()

    def connect(self):
        try:
            url = settings.SUPABASE_URL
            key = settings.SUPABASE_KEY
            if not url or not key:
                logger.warning("Supabase credentials missing. Client disabled.")
                return

            self.client = create_client(url, key)
            logger.info("✅ Supabase client initialized")
        except Exception as e:
            logger.error(f"❌ Supabase connection failed: {e}")

    @classmethod
    def get_client(cls) -> Client:
        if not cls._instance:
            cls._instance = SupabaseManager()
        return cls._instance.client

    def verify_user(self, email, password):
        """
        Verifies credentials by attempting to sign in.
        Returns (True, user_data) if valid, (False, error_msg) if not.
        """
        if not self.client:
            logger.warning("Supabase not connected. Skipping verification.")
            return True, "Skipped (No Connection)"

        try:
            res = self.client.auth.sign_in_with_password({"email": email, "password": password})
            if res.user:
                return True, res.user
            return False, "User not found"
        except Exception as e:
            logger.error(f"Auth Failed: {e}")
            return False, str(e)

supabase_client = SupabaseManager.get_client()
