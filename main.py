import sys
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger import setup_logging

def create_directories():
    """Create required application directories"""
    base_dir = Path(__file__).parent
    dirs = {
        'base': base_dir,
        'data': base_dir / 'data',
        'logs': base_dir / 'logs',
        'screenshots': base_dir / 'data' / 'screenshots',
        'audio': base_dir / 'data' / 'audio'
    }
    
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    
    return dirs

def main():
    """Main application entry point."""
    try:
        # Setup directories and logging
        dirs = create_directories()
        setup_logging(dirs['logs'])
        
        # Create application instance
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        # Create and show main window
        window = MainWindow(dirs)
        window.show()
        
        # Run application event loop
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Fatal error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()