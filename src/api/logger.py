"""
Logging configuration for the Backend API.

Sets up structured logging with appropriate levels and formatting for
debugging and error tracking.
"""

import logging
import sys
from src.api.config import APIConfig


def setup_logging():
    """
    Configure logging for the Backend API.
    
    Sets up root logger with console handler and configures log level
    based on APIConfig settings.
    """
    # Get log level from config
    log_level = getattr(logging, APIConfig.LOG_LEVEL.upper(), logging.INFO)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=APIConfig.LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific log levels for noisy libraries
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured with level: {APIConfig.LOG_LEVEL}")
    logger.info(f"API Configuration: {APIConfig.get_config_dict()}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name (typically __name__ of the module)
    
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
