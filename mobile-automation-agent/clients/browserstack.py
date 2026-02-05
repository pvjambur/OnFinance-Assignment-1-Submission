import logging
import requests
import json
from config.settings import settings
from typing import Dict, Any

logger = logging.getLogger(__name__)

class BrowserStackClient:
    BASE_URL = "https://api-cloud.browserstack.com/app-automate"

    def __init__(self):
        self.auth = (settings.BROWSERSTACK_USERNAME, settings.BROWSERSTACK_ACCESS_KEY)
        self.can_connect = bool(settings.BROWSERSTACK_USERNAME and settings.BROWSERSTACK_ACCESS_KEY)

    def upload_app(self, app_path: str) -> str:
        """Upload app to BrowserStack and get app_url"""
        if not self.can_connect:
            logger.warning("BS Credentials missing")
            return None
            
        try:
            url = f"{self.BASE_URL}/upload"
            files = {'file': open(app_path, 'rb')}
            response = requests.post(url, files=files, auth=self.auth)
            
            if response.status_code == 200:
                app_url = response.json().get('app_url')
                logger.info(f"✅ App uploaded: {app_url}")
                return app_url
            else:
                logger.error(f"Upload failed: {response.text}")
                return None
        except Exception as e:
            logger.error(f"BS Upload Error: {e}")
            return None

    def get_session_details(self, session_id: str) -> Dict[str, Any]:
        """Get details of a session"""
        if not self.can_connect:
            return {}
            
        try:
            url = f"{self.BASE_URL}/sessions/{session_id}.json"
            response = requests.get(url, auth=self.auth)
            return response.json()
        except Exception as e:
            logger.error(f"BS Session API Error: {e}")
            return {}

browserstack_client = BrowserStackClient()
