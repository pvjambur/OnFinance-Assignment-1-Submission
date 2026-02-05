import logging
from typing import Dict, Any, Optional
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from config.settings import settings
import time
import os
import yaml

logger = logging.getLogger(__name__)

class AppiumClient:
    def __init__(self):
        self.driver = None
        self.options = UiAutomator2Options()
        self.bs_config = {}
        
    def initialize_driver(self, app_url: Optional[str] = None):
        """Initialize Appium Driver for BrowserStack or Local"""
        try:
            # 1. Try Loading BrowserStack YAML
            self._load_yaml_config()
            
            if self.bs_config.get('userName') and self.bs_config.get('accessKey'):
                logger.info("🌍 Connecting to BrowserStack (via browserstack.yml)...")
                self._init_browserstack(app_url)
            elif settings.BROWSERSTACK_USERNAME and settings.BROWSERSTACK_ACCESS_KEY:
                logger.info("🌍 Connecting to BrowserStack (via .env)...")
                self._init_browserstack(app_url)
            else:
                logger.info("🏠 Connecting to Local Appium (Emulator/Device)...")
                self._init_local(app_url)
                
            logger.info("✅ Appium Driver Initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to initialize Appium Driver: {e}")
            self.driver = None
            return False

    def _load_yaml_config(self):
        """Load browserstack.yml if it exists"""
        yaml_path = settings.BASE_DIR / "browserstack.yml"
        if yaml_path.exists():
            try:
                with open(yaml_path, 'r') as f:
                    self.bs_config = yaml.safe_load(f) or {}
                logger.info(f"Loaded config from {yaml_path}")
            except Exception as e:
                 logger.warning(f"Failed to load browserstack.yml: {e}")

    def _init_browserstack(self, app_url: Optional[str]):
        # Prefer YAML config, fallback to Settings
        username = settings.BROWSERSTACK_USERNAME
        access_key = settings.BROWSERSTACK_ACCESS_KEY
        
        # Configure BrowserStack options
        bstack_options = {
            "userName": username,
            "accessKey": access_key,
            "projectName": self.bs_config.get('projectName', "Mobile Agent"),
            "buildName": self.bs_config.get('buildName', "agent-build-1"),
            "sessionName": "Agent Session"
        }
        
        self.options.set_capability('bstack:options', bstack_options)
        
        # Platform Config
        platforms = self.bs_config.get('platforms', [])
        if platforms and isinstance(platforms, list):
            platform = platforms[0]
            self.options.set_capability('platformName', platform.get('platformName', 'android'))
            self.options.set_capability('platformVersion', platform.get('platformVersion', '12.0'))
            self.options.set_capability('deviceName', platform.get('deviceName', 'Samsung Galaxy S22 Ultra'))
        else:
            self.options.set_capability('platformName', 'android')
            self.options.set_capability('platformVersion', '12.0') 
            self.options.set_capability('deviceName', 'Samsung Galaxy S22 Ultra')
        
        # --- NEW LOGIC START ---
        # Check for 'app' first
        config_app = self.bs_config.get('app')
        
        # Priority:
        # 1. 'app' provided at runtime args -> Native App Test
        # 2. 'app' in YAML -> Native App Test
        # 3. 'browserName' in YAML -> Mobile Web Test
        
        if app_url:
             self.options.set_capability('app', app_url)
             logger.info(f"📱 Testing App: {app_url}")
        elif config_app:
             self.options.set_capability('app', config_app)
             logger.info(f"📱 Testing App (from YAML): {config_app}")
        else:
             # If no app, check for 'browserName' in YAML
             browser_name = self.bs_config.get('browserName')
             if browser_name:
                 self.options.set_capability('browserName', browser_name)
                 logger.info(f"🌐 Testing Browser: {browser_name}")
                 # Ensure no 'app' capability is set if testing browser
             else:
                 logger.warning("⚠️ No 'app' OR 'browserName' found. BrowserStack connection may fail.")
        # --- NEW LOGIC END ---

        self.driver = webdriver.Remote(
            command_executor=settings.BROWSERSTACK_HUB,
            options=self.options
        )

    def _init_local(self, app_url: Optional[str]):
        # Local Capabilities
        self.options.set_capability('platformName', 'Android')
        self.options.set_capability('automationName', 'UiAutomator2')
        self.options.set_capability('deviceName', 'Android Emulator')
        self.options.set_capability('noReset', True) # Don't wipe app data
        
        # If user provides an app path/url, use it. 
        # Otherwise assume app is installed or handled manually.
        if app_url:
             self.options.set_capability('app', app_url)

        # Default local Appium URL
        url = "http://localhost:4723"
        
        self.driver = webdriver.Remote(
            command_executor=url,
            options=self.options
        )

    def capture_screenshot(self, filename: str = "latest_screenshot.png") -> str:
        """Capture screenshot and save to file"""
        if not self.driver:
            logger.warning("Driver not initialized, cannot screenshot.")
            return ""
            
        try:
            self.driver.save_screenshot(filename)
            logger.debug(f"📸 Screenshot saved: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return ""

    def execute_action(self, action_plan: Dict[str, Any]):
        """Execute action from ActionAgent"""
        if not self.driver:
            logger.warning("Driver not initialized, cannot execute action.")
            return

        action_type = action_plan.get('type')
        target = action_plan.get('target') # e.g. "login_button" or coordinates
        
        logger.info(f"🦾 Executing: {action_type} on {target}")
        
        try:
            if action_type == 'tap':
                self._handle_tap(action_plan)
            elif action_type == 'input':
                self._handle_input(action_plan)
            elif action_type == 'scroll':
                self._handle_scroll(action_plan)
            elif action_type == 'wait':
                time.sleep(2)
            else:
                logger.warning(f"Unknown action type: {action_type}")
        except Exception as e:
            logger.error(f"Action Execution Error: {e}")

    def _handle_tap(self, action: Dict[str, Any]):
        # Logic to tap based on coordinates or element ID
        # For this stage, we'll assume the LLM might return coordinates if Vision gave them,
        # or we might need to find by text.
        
        # Example: if coordinates provided
        coords = action.get('coordinates')
        if coords:
            x, y = coords
            self.driver.tap([(x, y)])
            return

        # Example: fallback to searching by text (unreliable but helpful)
        # element = self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().textContains("{target}")')
        # element.click()
        pass

    def _handle_input(self, action: Dict[str, Any]):
        text = action.get('value')
        # This requires the element to be focused or found first
        # For now, simplest is typically 'send keys to active element' or find by ID
        active_el = self.driver.switch_to.active_element
        if active_el:
            active_el.send_keys(text)

    def _handle_scroll(self, action: Dict[str, Any]):
        # Simple scroll down
        # Setup dimensions
        size = self.driver.get_window_size()
        start_x = size['width'] / 2
        start_y = size['height'] * 0.8
        end_x = size['width'] / 2
        end_y = size['height'] * 0.2
        
        self.driver.swipe(start_x, start_y, end_x, end_y, 400)

    def quit(self):
        if self.driver:
            self.driver.quit()

appium_client = AppiumClient()
