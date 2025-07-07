import logging
from pathlib import Path
from logging.handlers import RotatingFileHandler

def setup_logging(log_dir=None, level=logging.INFO):
    """Configure application logging."""
    logger = logging.getLogger()
    logger.setLevel(level)
    
    # Clear existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler if log directory is provided
    if log_dir and isinstance(log_dir, Path):
        log_file = log_dir / 'monitoring_tool.log'
        file_handler = RotatingFileHandler(
            log_file, maxBytes=1024*1024, backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger