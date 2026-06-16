"""
Universal YOLO Models Schemas
Supports: intrusion, people, security_threats, vehicle detection
Copy-paste friendly for adding new models
"""
from pydantic import BaseModel, validator
from typing import List, Optional, Dict, Any
from enum import Enum

class ModelType(str, Enum):
    """Supported YOLO model types"""
    INTRUSION = "intrusion"
    PEOPLE = "people" 
    SECURITY_THREATS = "security_threats"
    VEHICLE = "vehicle"

class DetectionRequest(BaseModel):
    """Universal detection request for any YOLO model"""
    image_data: str  # Base64 encoded image
    model_type: ModelType
    confidence: Optional[float] = 0.5
    iou_threshold: Optional[float] = 0.45
    
    @validator('image_data')
    def validate_image_data(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Image data cannot be empty')
        if len(v) < 100:  # Minimum base64 image size
            raise ValueError('Image data appears to be invalid')
        return v.strip()
    
    @validator('confidence')
    def validate_confidence(cls, v):
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError('Confidence must be between 0.0 and 1.0')
        return v
    
    @validator('iou_threshold')
    def validate_iou_threshold(cls, v):
        if v is not None and (v < 0.0 or v > 1.0):
            raise ValueError('IoU threshold must be between 0.0 and 1.0')
        return v

class Detection(BaseModel):
    """Single detection result"""
    class_id: int
    class_name: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]
    
class DetectionResponse(BaseModel):
    """Universal detection response for any YOLO model"""
    success: bool
    model_type: str
    detections: List[Detection]
    total_detections: int
    processing_time: float
    image_size: List[int]  # [width, height]
    message: Optional[str] = None

class ModelInfo(BaseModel):
    """Model information response"""
    model_type: str
    model_file: str
    classes: List[str]
    loaded: bool
    last_used: Optional[str] = None

class ModelsListResponse(BaseModel):
    """Response for listing all available models"""
    success: bool
    models: List[ModelInfo]
    total_models: int
