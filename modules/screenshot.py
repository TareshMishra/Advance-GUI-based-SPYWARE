from mss import mss
from pathlib import Path
from datetime import datetime
import os
from utils.logger import setup_logging

class ScreenshotCapture:
    """Class to capture and save screenshots."""
    
    def __init__(self):
        self.screenshot_dir = Path(__file__).parent.parent / 'data' / 'screenshots'
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.logger = setup_logging('screenshot')
        
    def capture(self, monitor=1):
        """Capture screenshot of specified monitor."""
        try:
            with mss() as sct:
                # Get monitor info
                monitor_info = sct.monitors[monitor]
                
                # Capture screenshot
                sct_img = sct.grab(monitor_info)
                
                # Generate filename
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = self.screenshot_dir / f"screenshot_{timestamp}.png"
                
                # Save the screenshot using mss's built-in to_png
                from mss.tools import to_png
                to_png(sct_img.rgb, sct_img.size, output=str(filename))
                
                self.logger.info(f"Screenshot saved to {filename}")
                return str(filename)
        except Exception as e:
            self.logger.error(f"Error capturing screenshot: {e}")
            raise

    def capture_all(self):
        """Capture screenshots of all monitors."""
        try:
            with mss() as sct:
                files = []
                for i, monitor in enumerate(sct.monitors[1:], 1):
                    sct_img = sct.grab(monitor)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    filename = self.screenshot_dir / f"screenshot_monitor{i}_{timestamp}.png"
                    
                    from mss.tools import to_png
                    to_png(sct_img.rgb, sct_img.size, output=str(filename))
                    
                    files.append(str(filename))
                self.logger.info(f"Captured screenshots to {files}")
                return files
        except Exception as e:
            self.logger.error(f"Error capturing all screenshots: {e}")
            raise