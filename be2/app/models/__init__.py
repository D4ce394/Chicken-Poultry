"""
Models package
"""
try:
    from .auth import User, get_admin_by_username, add_admin
    from .models import DetectionResult, ModelMetadata, save_detection_result, get_detection_history, update_model_metadata
    __all__ = ["User", "get_admin_by_username", "add_admin", 
               "DetectionResult", "ModelMetadata", "save_detection_result", 
               "get_detection_history", "update_model_metadata"]
except ImportError as e:
    print(f"Warning: Could not import models: {e}")
    __all__ = []

