"""
Universal YOLO API Template - INTRUSION MODEL
Copy-paste this file and change MODEL_TYPE for new models

For new models:
1. Copy this file
2. Rename to [model_name]_api.py  
3. Change MODEL_TYPE = "your_model_name"
4. Import in main.py
"""

from fastapi import APIRouter, HTTPException
from app.services.models_service import yolo_service
from app.schemas.models_schemas import DetectionRequest, DetectionResponse, ModelsListResponse

# 🔧 CHANGE THIS FOR NEW MODELS
MODEL_TYPE = "intrusion"

router = APIRouter()

@router.post("/detect", response_model=DetectionResponse)
async def detect_intrusion(request: DetectionRequest):
    """
    Detect intrusion in image
    
    Copy-paste template - only MODEL_TYPE changes for different models
    """
    try:
        # Override model type to ensure correct model is used
        request.model_type = MODEL_TYPE
        
        result = await yolo_service.detect_objects(
            model_type=MODEL_TYPE,
            image_data=request.image_data,
            confidence=request.confidence or 0.5,
            iou_threshold=request.iou_threshold or 0.45
        )
        
        return DetectionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Intrusion detection failed: {str(e)}")

@router.get("/info")
async def get_intrusion_model_info():
    """
    Get intrusion model information
    
    Copy-paste template - only MODEL_TYPE changes
    """
    try:
        return await yolo_service.get_model_info(MODEL_TYPE)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_intrusion_history(limit: int = 100):
    """
    Get intrusion detection history
    
    Copy-paste template - only MODEL_TYPE changes
    """
    try:
        return await yolo_service.get_detection_history(MODEL_TYPE, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/load")
async def load_intrusion_model():
    """
    Load intrusion model into memory
    
    Copy-paste template - only MODEL_TYPE changes
    """
    try:
        success = await yolo_service.load_model(MODEL_TYPE)
        if success:
            return {"success": True, "message": f"{MODEL_TYPE} model loaded successfully"}
        else:
            raise HTTPException(status_code=500, detail=f"Failed to load {MODEL_TYPE} model")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))