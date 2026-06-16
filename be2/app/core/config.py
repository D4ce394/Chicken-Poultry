"""
Global configuration for AI-FRSS Modular WebSocket Surveillance API v2.0
Following be2v2.0 pattern with enhanced settings
"""

import os
from typing import List

class Settings:
    """Application settings following modular architecture"""
    
    # Core Application Settings
    PROJECT_NAME = "AI-FRSS Modular WebSocket Surveillance API"
    VERSION = "2.0.0"
    DEBUG = True
    ENV = os.getenv("ENV", "development")
    
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    RELOAD = True
    
    # YOLO Models Configuration
    YOLO_MODELS_PATH = "app/yolo_models"
    DEFAULT_CONFIDENCE = 0.5
    DEFAULT_IOU_THRESHOLD = 0.45
    MAX_DETECTIONS = 100
    
    # Supported model types
    SUPPORTED_MODELS = ["intrusion", "people", "security_threats", "vehicle"]
    
    # Image Processing
    MAX_IMAGE_WIDTH = 1280
    MAX_IMAGE_HEIGHT = 720
    ALLOWED_IMAGE_FORMATS = ["jpg", "jpeg", "png", "bmp", "tiff"]
    
    # Performance Settings
    PRELOAD_MODELS = ["intrusion"]  # Models to preload at startup
    MODEL_CACHE_SIZE = 4
    INFERENCE_DEVICE = "cpu"  # or 'cuda'
    
    # WebSocket Configuration
    MAX_WEBSOCKET_CONNECTIONS = 1000
    WEBSOCKET_TIMEOUT = 300  # seconds
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Database (optional)
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_frss.db")
    DATABASE_ECHO = DEBUG
    
    # Security
    JWT_SECRET = os.getenv("JWT_SECRET", "ai-frss-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    
    # CORS Settings
    ALLOWED_ORIGINS = ["*"]  # Configure appropriately for production
    ALLOWED_METHODS = ["*"]
    ALLOWED_HEADERS = ["*"]

# Global settings instance
settings = Settings()

# Export for easy access
__all__ = ["settings", "Settings"]
