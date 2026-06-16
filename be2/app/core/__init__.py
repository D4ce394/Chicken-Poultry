"""
Core utilities, config, and shared logic for AI-FRSS backend v2.0
Modular architecture with dynamic WebSocket handler loading
"""

import os
from .config import settings

PROJECT_NAME = settings.PROJECT_NAME
VERSION = settings.VERSION
ENV = os.getenv("ENV", "development")

__all__ = ["settings", "PROJECT_NAME", "VERSION", "ENV"]
