import logging
import time
import os
from typing import Dict, Any, Optional
from appium import webdriver
from appium.options.android import UiAutomator2Options
from PIL import Image

logger = logging.getLogger(__name__)

class AppiumClient:
    def __init__(self):
        self.driver = None
        self.options = UiAutomator2Options()
        self.img_width = 0
        self.img_height = 0

    def initialize_driver(self, app_url: Optional[str] = None):
        """Initialize Appium Driver with Auto-Path Detection"""
        try:
            android_home = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
            if not android_home:
                logger.error("❌ CRITICAL: 'ANDROID_HOME' is not set!")
                return False

            logger.info("🏠 Connecting to Local Appium (Emulator)...")
            
            # Setup Capabilities
            self.options.set_capability('platformName', 'Android')
            self.options.set_capability('automationName', 'UiAutomator2')
            self.options.set_capability('deviceName', 'Android Emulator') 
            self.options.set_capability('noReset', True)
            self.options.set_capability('newCommandTimeout', 300)
            if app_url: self.options.set_capability('app', app_url)

            # --- FIX: Try both URL paths (Appium 2 vs Legacy) ---
            possible_urls = [
                "http://127.0.0.1:4723",          # Appium 2.0 Standard (Root)
                "http://127.0.0.1:4723/wd/hub"    # Legacy / Default for some clients
            ]

            connection_success = False
            for url in possible_urls:
                try:
                    logger.info(f"Trying connection at: {url} ...")
                    self.driver = webdriver.Remote(command_executor=url, options=self.options)
                    logger.info(f"✅ Appium Driver Initialized at {url}")
                    connection_success = True
                    break # Stop trying if successful
                except Exception as e:
                    logger.warning(f"⚠️ Failed to connect to {url}: {str(e)[:100]}...")
            
            if not connection_success:
                logger.error("❌ All connection attempts failed.")
                self.driver = None
                return False

            return True

        except Exception as e:
            logger.error(f"❌ Connection Failed: {e}")
            self.driver = None
            return False

    def capture_screenshot(self, filename: str = "latest_screenshot.png") -> str:
        if not self.driver: return "" 
        try:
            self.driver.save_screenshot(filename)
            with Image.open(filename) as img:
                self.img_width, self.img_height = img.size
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
        if not coords: return
        x, y = coords

        if self.img_width > 0 and self.img_height > 0:
            window = self.driver.get_window_size()
            scale_x = window['width'] / self.img_width
            scale_y = window['height'] / self.img_height
            final_x = int(x * scale_x)
            final_y = int(y * scale_y)
            self.driver.tap([(final_x, final_y)])
        else:
            self.driver.tap([(x, y)])

    def _handle_input(self, action: Dict[str, Any]):
        text = action.get('value')
        if text: os.system(f"adb shell input text '{text}'")

    def _handle_scroll(self, action: Dict[str, Any]):
        size = self.driver.get_window_size()
        self.driver.swipe(size['width']/2, size['height']*0.8, size['width']/2, size['height']*0.2, 400)

    def execute_system_command(self, command: str):
        """Execute Android System Commands (Safe vs Unsafe)"""
        if not command: return
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
            elif cmd == 'notification' or cmd == 'notifications': self.driver.open_notifications()
            
            # ADB Commands (Bypassing Appium Driver to avoid 404s)
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