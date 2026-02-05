import logging
import time
import os
from typing import Dict, Any, Optional
from appium import webdriver
from appium.options.android import UiAutomator2Options
from PIL import Image  # Required for reading screenshot dimensions

logger = logging.getLogger(__name__)

class AppiumClient:
    def __init__(self):
        self.driver = None
        self.options = UiAutomator2Options()
        # Store dimensions to calculate scaling ratio
        self.img_width = 0
        self.img_height = 0

    def initialize_driver(self, app_url: Optional[str] = None):
        """Initialize Appium Driver (Local Priority)"""
        try:
            android_home = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
            if not android_home:
                logger.error("❌ CRITICAL: 'ANDROID_HOME' is not set!")
                return False

            logger.info("🏠 Connecting to Local Appium (Emulator)...")
            self._init_local(app_url)
            logger.info("✅ Appium Driver Initialized Successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Connection Failed: {e}")
            self.driver = None
            return False

    def _init_local(self, app_url: Optional[str]):
        self.options.set_capability('platformName', 'Android')
        self.options.set_capability('automationName', 'UiAutomator2')
        self.options.set_capability('deviceName', 'Android Emulator') 
        self.options.set_capability('noReset', True)
        self.options.set_capability('newCommandTimeout', 300)
        
        if app_url:
             self.options.set_capability('app', app_url)

        # 3. Connect to Server (Default Localhost)
        url = "http://127.0.0.1:4723" 
        self.driver = webdriver.Remote(command_executor=url, options=self.options)

    def capture_screenshot(self, filename: str = "latest_screenshot.png") -> str:
        """Capture screenshot and RECORD DIMENSIONS for scaling"""
        if not self.driver: return "" 
        try:
            self.driver.save_screenshot(filename)
            
            # --- NEW: Read dimensions to calculate scale ratio ---
            with Image.open(filename) as img:
                self.img_width, self.img_height = img.size
            # ---------------------------------------------------
            
            return filename
        except Exception:
            return ""

    def execute_action(self, action_plan: Dict[str, Any]):
        if not self.driver: return

        if 'action' in action_plan and isinstance(action_plan['action'], dict):
            action_data = action_plan['action']
        else:
            action_data = action_plan

        action_type = action_data.get('type') or action_data.get('action') 
        if action_type == 'navigate': action_type = 'tap' 
        
        logger.info(f"📱 Action: {action_type} | Data: {action_data}")
        
        try:
            if action_type in ['tap', 'click']:
                self._handle_tap(action_data)
            elif action_type in ['input', 'type', 'write']:
                self._handle_input(action_data)
            elif action_type in ['swipe', 'scroll']:
                self._handle_scroll(action_data)
            elif action_type == 'system':
                self.execute_system_command(action_data.get('command') or action_data.get('value'))
            elif action_type == 'wait':
                time.sleep(2)
            elif action_type == 'finish':
                logger.info("🎉 Task finished.")
        except Exception as e:
            logger.error(f"❌ Action Error: {e}")

    def _handle_tap(self, action: Dict[str, Any]):
        coords = action.get('coordinates')
        if not coords:
            logger.warning("Tap requested but no coordinates provided.")
            return

        x, y = coords

        # --- NEW: AUTOMATIC SCALING (Pixel -> Point) ---
        if self.img_width > 0 and self.img_height > 0:
            # Get Logical Window Size (Points)
            window = self.driver.get_window_size()
            win_w = window['width']
            win_h = window['height']
            
            # Calculate Ratio (e.g. 411 / 1080 = 0.38)
            scale_x = win_w / self.img_width
            scale_y = win_h / self.img_height
            
            # Scale coordinates
            final_x = int(x * scale_x)
            final_y = int(y * scale_y)
            
            logger.info(f"🎯 Scaling Tap: ({x}, {y}) -> ({final_x}, {final_y})")
            self.driver.tap([(final_x, final_y)])
        else:
            # Fallback if no screenshot taken yet
            self.driver.tap([(x, y)])

    def _handle_input(self, action: Dict[str, Any]):
        text = action.get('value')
        if text:
            os.system(f"adb shell input text '{text}'")

    def _handle_scroll(self, action: Dict[str, Any]):
        size = self.driver.get_window_size()
        start_x = size['width'] / 2
        start_y = size['height'] * 0.8
        end_y = size['height'] * 0.2
        self.driver.swipe(start_x, start_y, start_x, end_y, 400)

    def execute_system_command(self, command: str):
        if not self.driver or not command: return
        cmd = command.lower()
        logger.info(f"📱 System Command: {cmd}")

        try:
            if cmd == 'home': self.driver.press_keycode(3)
            elif cmd == 'back': self.driver.press_keycode(4)
            elif cmd == 'recents': self.driver.press_keycode(187)
            elif cmd == 'volume_up': self.driver.press_keycode(24)
            elif cmd == 'volume_down': self.driver.press_keycode(25)
            elif cmd == 'enter': self.driver.press_keycode(66)
            elif cmd == 'power': self.driver.press_keycode(26)
            elif cmd == 'notification' or cmd == 'notifications':
                self.driver.open_notifications()
            elif cmd == 'restart' or cmd == 'reboot':
                os.system("adb shell reboot")
            elif cmd == 'shutdown' or cmd == 'turn off':
                os.system("adb shell reboot -p")
            elif cmd == 'torch':
                os.system("adb shell cmd statusbar expand-settings")
            else:
                logger.warning(f"Unknown system command: {cmd}")
        except Exception as e:
            logger.error(f"System Command Error: {e}")

    def quit(self):
        if self.driver:
            try: self.driver.quit()
            except: pass

appium_client = AppiumClient()