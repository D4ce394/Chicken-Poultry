"""
Universal YOLO Models Database Schema
Supports: intrusion, people, security_threats, vehicle detection
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base
import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.services.database_service import database_service

# Use the same Base as auth.py
from .auth import Base

class DetectionResult(Base):
    """Universal table for storing YOLO detection results"""
    __tablename__ = "detection_results"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    model_type = Column(String(50), nullable=False, index=True)  # intrusion, people, etc
    image_name = Column(String(255), nullable=True)
    detections = Column(JSON, nullable=False)  # Store detection results as JSON
    total_detections = Column(Integer, default=0)
    processing_time = Column(Float, nullable=False)
    confidence_threshold = Column(Float, default=0.5)
    iou_threshold = Column(Float, default=0.45)
    image_size = Column(JSON, nullable=True)  # [width, height]
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ModelMetadata(Base):
    """Metadata for YOLO models"""
    __tablename__ = "model_metadata"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    model_type = Column(String(50), unique=True, nullable=False, index=True)
    model_file = Column(String(255), nullable=False)
    classes = Column(JSON, nullable=False)  # List of class names
    is_loaded = Column(Boolean, default=False)
    last_used = Column(DateTime(timezone=True), nullable=True)
    total_detections = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# Database operations for models
async def save_detection_result(model_type: str, detections: list, processing_time: float, 
                              confidence: float = 0.5, iou: float = 0.45, 
                              image_size: list = None, image_name: str = None):
    """Save detection result to database"""
    try:
        query = """
        INSERT INTO detection_results (id, model_type, image_name, detections, total_detections,
                                     processing_time, confidence_threshold, iou_threshold, image_size)
        VALUES (:id, :model_type, :image_name, :detections, :total_detections,
                :processing_time, :confidence_threshold, :iou_threshold, :image_size)
        """
        values = {
            "id": str(uuid.uuid4()),
            "model_type": model_type,
            "image_name": image_name,
            "detections": detections,
            "total_detections": len(detections),
            "processing_time": processing_time,
            "confidence_threshold": confidence,
            "iou_threshold": iou,
            "image_size": image_size
        }
        await database_service.execute_query(query, values)
        return True
    except Exception as e:
        # Silently fail if database is unavailable - detection still works
        return False

async def get_detection_history(model_type: str = None, limit: int = 100):
    """Get detection history"""
    try:
        if model_type:
            query = """
            SELECT * FROM detection_results 
            WHERE model_type = :model_type 
            ORDER BY created_at DESC 
            LIMIT :limit
            """
            return await database_service.fetch_all(query, {"model_type": model_type, "limit": limit})
        else:
            query = "SELECT * FROM detection_results ORDER BY created_at DESC LIMIT :limit"
            return await database_service.fetch_all(query, {"limit": limit})
    except Exception as e:
        # Silently fail if database is unavailable
        return []

async def update_model_metadata(model_type: str, model_file: str, classes: list):
    """Update or insert model metadata"""
    try:
        # Check if exists
        existing = await database_service.fetch_one(
            "SELECT id FROM model_metadata WHERE model_type = :model_type",
            {"model_type": model_type}
        )
        
        if existing:
            query = """
            UPDATE model_metadata 
            SET model_file = :model_file, classes = :classes, last_used = NOW(), updated_at = NOW()
            WHERE model_type = :model_type
            """
        else:
            query = """
            INSERT INTO model_metadata (id, model_type, model_file, classes, is_loaded)
            VALUES (:id, :model_type, :model_file, :classes, :is_loaded)
            """
        
        values = {
            "model_type": model_type,
            "model_file": model_file,
            "classes": classes
        }
        
        if not existing:
            values["id"] = str(uuid.uuid4())
            values["is_loaded"] = True
            
        await database_service.execute_query(query, values)
        return True
    except Exception as e:
        # Silently fail if database is unavailable - models still work
        return False

# Export commonly used items
__all__ = ["DetectionResult", "ModelMetadata", "save_detection_result", 
           "get_detection_history", "update_model_metadata"]