"""
Configuration settings for the Backend API.

Defines configuration parameters for API server, CORS, and processing limits.
Supports environment variable overrides for flexible deployment.

Requirements: 10.1, 10.2, 10.3
"""

import os


class APIConfig:
    """
    Configuration class for Backend API settings.
    
    All settings can be overridden via environment variables for
    development, testing, and production deployments.
    """
    
    # Server settings
    HOST = os.getenv("API_HOST", "localhost")
    PORT = int(os.getenv("API_PORT", "5000"))
    DEBUG = os.getenv("API_DEBUG", "False").lower() == "true"
    
    # CORS settings - supports wildcard ports for development
    # Production should use specific origins
    CORS_ORIGINS = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:*,http://127.0.0.1:*"
    ).split(",")
    
    # Image processing limits
    MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", str(10 * 1024 * 1024)))  # 10 MB default
    MAX_IMAGE_DIMENSION = int(os.getenv("MAX_IMAGE_DIMENSION", "4096"))  # 4096 pixels default
    
    # Session settings
    SESSION_TIMEOUT = int(os.getenv("SESSION_TIMEOUT", "3600"))  # 1 hour default
    
    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Model settings
    MODEL_CHECKPOINT_PATH = os.getenv("MODEL_CHECKPOINT_PATH", "models/best_model.pth")
    
    @classmethod
    def get_config_dict(cls):
        """Get configuration as dictionary."""
        return {
            "host": cls.HOST,
            "port": cls.PORT,
            "debug": cls.DEBUG,
            "cors_origins": cls.CORS_ORIGINS,
            "max_image_size": cls.MAX_IMAGE_SIZE,
            "max_image_dimension": cls.MAX_IMAGE_DIMENSION,
            "session_timeout": cls.SESSION_TIMEOUT,
            "log_level": cls.LOG_LEVEL,
            "model_checkpoint_path": cls.MODEL_CHECKPOINT_PATH
        }
