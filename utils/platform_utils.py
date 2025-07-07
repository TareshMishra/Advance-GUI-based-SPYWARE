import platform
import subprocess
import os
from typing import Tuple

def get_os() -> str:
    """Get the current operating system."""
    system = platform.system().lower()
    if system == 'windows':
        return 'windows'
    elif system == 'linux':
        return 'linux'
    elif system == 'darwin':
        return 'macos'
    return 'unknown'

def run_command(command: list) -> Tuple[str, str, int]:
    """
    Run a system command and return the output.
    
    Args:
        command: List of command and arguments
        
    Returns:
        Tuple of (stdout, stderr, returncode)
    """
    try:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()
        return stdout, stderr, process.returncode
    except Exception as e:
        return "", str(e), -1

def is_admin() -> bool:
    """Check if the current user has admin/root privileges."""
    try:
        if get_os() == 'windows':
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.getuid() == 0
    except Exception:
        return False