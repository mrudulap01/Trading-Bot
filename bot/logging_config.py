import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logging(log_level: int = logging.INFO) -> logging.Logger:
    """
    Sets up structured, centralized logging for the entire application.
    
    Creates the 'logs' directory if it doesn't exist and configures
    logging to output to both the console and a rotating log file.
    
    Args:
        log_level (int): The logging level to use (default: logging.INFO).
        
    Returns:
        logging.Logger: The configured root logger.
    """
    # Resolve project root assuming this file is in bot/
    project_root = Path(__file__).resolve().parent.parent
    logs_dir = project_root / 'logs'
    log_file = logs_dir / 'trading.log'
    
    # Create logs directory automatically if missing
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    # Define the log format: timestamp | level | message
    # Example: 2026-06-03 10:45:21 | INFO | Market order placed successfully
    log_format = "%(asctime)s | %(levelname)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    formatter = logging.Formatter(fmt=log_format, datefmt=date_format)
    
    # Configure Root Logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Clear existing handlers to prevent duplicate logs if called multiple times
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
        
    # File Handler - using RotatingFileHandler for production-quality logging
    # Rotates at 10 MB and keeps up to 5 old backups
    file_handler = RotatingFileHandler(
        log_file, 
        maxBytes=10 * 1024 * 1024, 
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    
    # Add handlers to the root logger
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    return root_logger

def get_logger(name: str) -> logging.Logger:
    """
    Retrieves a logger with the given name.
    
    This is a reusable method to get a properly named logger for any module.
    Ensure `setup_logging()` has been called once at the start of the application.
    
    Args:
        name (str): The name of the logger, typically passed as __name__.
        
    Returns:
        logging.Logger: The configured logger object for the specified name.
    """
    return logging.getLogger(name)
