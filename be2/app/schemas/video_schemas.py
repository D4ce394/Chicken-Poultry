"""
Video Detection Schemas
Pydantic models for video processing APIs
"""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    EXTRACTING_FRAMES = "extracting_frames"
    PROCESSING_INTRUSION = "processing_intrusion"
    PROCESSING_PEOPLE = "processing_people"
    PROCESSING_SECURITY_THREATS = "processing_security_threats"
    PROCESSING_VEHICLE = "processing_vehicle"
    COMPLETED = "completed"
    FAILED = "failed"

class VideoUploadRequest(BaseModel):
    """Request for video upload processing"""
    model_types: List[str] = Field(default=["intrusion"], description="Models to run on video")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Detection confidence threshold")
    iou_threshold: float = Field(default=0.45, ge=0.0, le=1.0, description="IoU threshold for NMS")
    frame_skip: int = Field(default=30, ge=1, le=300, description="Process every Nth frame")
    
    @validator('model_types')
    def validate_models(cls, v):
        valid_models = ['intrusion', 'people', 'security_threats', 'vehicle']
        for model in v:
            if model not in valid_models:
                raise ValueError(f"Invalid model type: {model}. Valid options: {valid_models}")
        return v

class VideoMetadata(BaseModel):
    """Video file metadata"""
    fps: float
    frame_count: int
    width: int
    height: int
    duration_seconds: float
    duration_formatted: str

class VideoJobResponse(BaseModel):
    """Response for video upload job"""
    job_id: str
    status: ProcessingStatus
    filename: str
    metadata: VideoMetadata
    estimated_completion: datetime

class JobStatusResponse(BaseModel):
    """Job status response"""
    job_id: str
    status: ProcessingStatus
    updated_at: datetime
    results: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class VideoDetectionSummary(BaseModel):
    """Summary of video detection results"""
    total_models_processed: int
    models: Dict[str, Dict[str, Any]]

class VideoResultsResponse(BaseModel):
    """Complete video processing results"""
    job_id: str
    processed_at: datetime
    summary: VideoDetectionSummary
    detailed_results: Dict[str, List[Dict[str, Any]]]

# Real-time WebSocket schemas
class WebSocketMessage(BaseModel):
    """Base WebSocket message"""
    type: str
    data: Optional[Dict[str, Any]] = None
    frame_id: Optional[str] = None
    timestamp: Optional[str] = None

class FrameMessage(WebSocketMessage):
    """Frame data for real-time processing"""
    type: str = "frame"
    data: str = Field(description="Base64 encoded frame data")
    frame_id: str = Field(description="Unique frame identifier")

class ConfigMessage(WebSocketMessage):
    """Configuration update message"""
    type: str = "config"
    data: Dict[str, Any] = Field(description="Configuration parameters")

class DetectionResultMessage(WebSocketMessage):
    """Detection result message"""
    type: str = "detection_result"
    results: Dict[str, Any]
    stats: Dict[str, Any]

# CCTV Camera schemas
class CameraConfig(BaseModel):
    """CCTV camera configuration"""
    models: List[str] = Field(default=["intrusion", "people"], description="Models to run")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    iou_threshold: float = Field(default=0.45, ge=0.0, le=1.0)
    detection_interval: float = Field(default=2.0, ge=0.1, le=60.0, description="Seconds between detections")
    alert_threshold: int = Field(default=1, ge=0, description="Min detections to trigger alert")
    recording: bool = Field(default=False, description="Save detection frames")
    save_frames: bool = Field(default=False, description="Save frames with detections")

class AddCameraRequest(BaseModel):
    """Request to add new camera"""
    stream_url: str = Field(description="RTSP/HTTP stream URL")
    name: Optional[str] = Field(None, description="Camera display name")
    config: Optional[CameraConfig] = Field(default_factory=CameraConfig)

class CameraInfo(BaseModel):
    """Camera information"""
    camera_id: str
    name: str
    stream_url: str
    is_active: bool
    config: CameraConfig
    stats: Dict[str, Any]

class CameraListResponse(BaseModel):
    """List of cameras response"""
    cameras: List[CameraInfo]
    total_count: int

class DetectionEvent(BaseModel):
    """Detection event from CCTV"""
    timestamp: datetime
    camera_id: str
    camera_name: str
    total_detections: int
    results: Dict[str, Any]
    frame_data: Optional[str] = None

class SystemStatusResponse(BaseModel):
    """CCTV system status"""
    is_monitoring: bool
    total_cameras: int
    active_cameras: int
    total_detections: int
    cameras: List[CameraInfo]

class DetectionHistoryResponse(BaseModel):
    """Detection history response"""
    events: List[DetectionEvent]
    total_count: int
    camera_id: Optional[str] = None
