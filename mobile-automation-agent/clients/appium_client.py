import logging
from typing import Dict, Any, Optional
from appium import webdriver
from appium.options.android import UiAutomator2Options
from config.settings import settings
import time
import os

logger = logging.getLogger(__name__)

class AppiumClient:
    def __init__(self):
        self.driver = None
        self.options = UiAutomator2Options()

    def initialize_driver(self, app_url: Optional[str] = None):
        """Initialize Appium Driver (Local Priority)"""
        try:
            # --- DIAGNOSTIC: Check Environment Variables ---
            android_home = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
            if not android_home:
                logger.error("❌ CRITICAL: 'ANDROID_HOME' is not set!")
                logger.error("👉 Step 1: Open System Env Variables -> New -> Name: ANDROID_HOME -> Value: C:\\Users\\YOUR_USER\\AppData\\Local\\Android\\Sdk")
                logger.error("👉 Step 2: RESTART your terminal/VS Code.")
                return False
            else:
                logger.info(f"✅ Found ANDROID_HOME: {android_home}")

            # --- Initialize Local Connection ---
            logger.info("🏠 Connecting to Local Appium (Emulator)...")
            self._init_local(app_url)
            
            logger.info("✅ Appium Driver Initialized Successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Connection Failed: {e}")
            logger.error("💡 TIP: Ensure 'appium' is running in a separate terminal.")
            self.driver = None
            return False

    def _init_local(self, app_url: Optional[str]):
        """Configure Local Emulator Capabilities"""
        # 1. Capabilities
        self.options.set_capability('platformName', 'Android')
        self.options.set_capability('automationName', 'UiAutomator2')
        self.options.set_capability('deviceName', 'Android Emulator') 
        self.options.set_capability('noReset', True) # Don't wipe app data
        self.options.set_capability('newCommandTimeout', 300)
        
        # 2. App Handling
        if app_url:
             self.options.set_capability('app', app_url)
             logger.info(f"📱 App Path: {app_url}")

        # 3. Connect to Server
        # NOTE: If Appium says it's listening on 192.168.1.8, change this line.
        # Otherwise, 127.0.0.1 is the standard default.
        url = "http://127.0.0.1:4723" 
        
        self.driver = webdriver.Remote(command_executor=url, options=self.options)

    def capture_screenshot(self, filename: str = "latest_screenshot.png") -> str:
        """Capture screenshot safely"""
        if not self.driver:
            return "" 
        try:
            self.driver.save_screenshot(filename)
            logger.debug(f"📸 Screenshot saved: {filename}")
            return filename
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return ""

    def execute_action(self, action_plan: Dict[str, Any]):
        """Execute action with robust JSON parsing"""
        if not self.driver:
            logger.warning("⚠️ Driver not active, cannot execute action.")
            return

        # --- FIX: Handle different JSON formats from AI ---
        # Case A: {'action': {'type': 'tap', ...}} (Nested)
        # Case B: {'type': 'tap', ...} (Flat)
        
        if 'action' in action_plan and isinstance(action_plan['action'], dict):
            action_data = action_plan['action']
        else:
            action_data = action_plan

        # Extract type safely
        action_type = action_data.get('type') or action_data.get('action') 
        
        # Normalize synonyms
        if action_type == 'navigate': action_type = 'tap' 
        
        logger.info(f"🦾 Executing Action: {action_type} | Data: {action_data}")
        
        try:
            if action_type in ['tap', 'click']:
                self._handle_tap(action_data)
            elif action_type in ['input', 'type', 'write']:
                self._handle_input(action_data)
            elif action_type in ['swipe', 'scroll']:
                self._handle_scroll(action_data)
            elif action_type == 'wait':
                time.sleep(2)
            elif action_type == 'finish':
                logger.info("🎉 Task finished.")
            else:
                logger.warning(f"⚠️ Unknown action type: {action_type}")
        except Exception as e:
            logger.error(f"❌ Action Execution Error: {e}")

    def _handle_tap(self, action: Dict[str, Any]):
        coords = action.get('coordinates')
        if coords:
            x, y = coords
            self.driver.tap([(x, y)])
        else:
            logger.warning("Tap requested but no coordinates provided.")

    def _handle_input(self, action: Dict[str, Any]):
        text = action.get('value') or action.get('text')
        if text:
            try:
                # Try standard Appium input first
                active_el = self.driver.switch_to.active_element
                active_el.send_keys(text)
            except:
                # Fallback to ADB injection (faster/more reliable for emulators)
                logger.info("Using ADB fallback for text input")
                os.system(f"adb shell input text '{text}'")

    def _handle_scroll(self, action: Dict[str, Any]):
        direction = action.get('direction', 'down')
        size = self.driver.get_window_size()
        width = size['width']
        height = size['height']
        
        start_x = width / 2
        end_x = width / 2
        
        if direction == 'down':
            start_y = height * 0.8
            end_y = height * 0.2
        else: # up
            start_y = height * 0.2
            end_y = height * 0.8
            
        self.driver.swipe(start_x, start_y, end_x, end_y, 400)

    def quit(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

appium_client = AppiumClient()