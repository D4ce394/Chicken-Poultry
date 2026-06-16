"""
Mobile Vehicle Detection API
Simplified vehicle detection endpoints for mobile applications
"""
from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import Optional, List
import base64

from app.services.models_service import yolo_service

router = APIRouter()

class MobileDetectionRequest(BaseModel):
    image_base64: str
    confidence: Optional[float] = 0.5

class MobileDetectionResponse(BaseModel):
    success: bool
    detections: List[dict]
    total_objects: int
    processing_time: float

@router.post("/detect", response_model=MobileDetectionResponse)
async def detect_vehicle_mobile(request: MobileDetectionRequest):
    """Mobile-optimized vehicle detection"""
    try:
        result = await yolo_service.detect_objects(
            model_type="vehicle",
            image_data=request.image_base64,
            confidence=request.confidence,
            iou_threshold=0.45
        )
        
        # Simplify response for mobile
        mobile_detections = []
        for detection in result.get("detections", []):
            mobile_detections.append({
                "class": detection.get("class_name", "vehicle"),
                "confidence": round(detection.get("confidence", 0), 2),
                "bbox": detection.get("bbox", [])
            })
        
        return MobileDetectionResponse(
            success=result.get("success", False),
            detections=mobile_detections,
            total_objects=len(mobile_detections),
            processing_time=round(result.get("processing_time", 0), 3)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Vehicle detection failed: {str(e)}")

@router.post("/detect/upload")
async def detect_vehicle_upload(file: UploadFile = File(...)):
    """Vehicle detection via file upload (mobile)"""
    try:
        # Read and convert to base64
        content = await file.read()
        if len(content) > 5 * 1024 * 1024:  # 5MB limit
            raise HTTPException(status_code=400, detail="File too large (max 5MB)")
        
        image_base64 = base64.b64encode(content).decode('utf-8')
        
        request = MobileDetectionRequest(image_base64=image_base64)
        return await detect_vehicle_mobile(request)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/info")
async def get_vehicle_model_info():
    """Get vehicle model information for mobile"""
    try:
        info = await yolo_service.get_model_info("vehicle")
        return {
            "success": True,
            "model_type": "vehicle",
            "classes": info.get("classes", []),
            "loaded": info.get("loaded", False)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))