"""
Parallel YOLO Detection API - All models at once for fast results
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
import asyncio
import time
import json
from typing import Optional

router = APIRouter()

class YOLOAllRequest(BaseModel):
    image_data: Optional[str] = None
    confidence_threshold: float = 0.5
    include_models: list = ["intrusion", "people", "security_threats", "vehicle"]

# Mock YOLO functions (same as in websocket_handler)
async def detect_intrusion_api(image_data, confidence=0.5):
    await asyncio.sleep(0.1)
    return {
        "model": "intrusion",
        "detections": [
            {"class": "person", "confidence": 0.85, "bbox": [100, 100, 200, 200]},
            {"class": "suspicious_activity", "confidence": 0.72, "bbox": [300, 150, 400, 250]}
        ],
        "processing_time": 0.1
    }

async def detect_people_api(image_data, confidence=0.5):
    await asyncio.sleep(0.12)
    return {
        "model": "people",
        "detections": [
            {"class": "person", "confidence": 0.92, "bbox": [120, 80, 220, 280]},
            {"class": "person", "confidence": 0.87, "bbox": [350, 90, 450, 290]}
        ],
        "count": 2,
        "processing_time": 0.12
    }

async def detect_security_threats_api(image_data, confidence=0.5):
    await asyncio.sleep(0.08)
    return {
        "model": "security_threats",
        "detections": [
            {"class": "weapon", "confidence": 0.68, "bbox": [200, 200, 250, 300]},
        ],
        "threat_level": "medium",
        "processing_time": 0.08
    }

async def detect_vehicle_api(image_data, confidence=0.5):
    await asyncio.sleep(0.11)
    return {
        "model": "vehicle",
        "detections": [
            {"class": "car", "confidence": 0.94, "bbox": [50, 300, 300, 500]},
            {"class": "motorcycle", "confidence": 0.81, "bbox": [400, 350, 500, 450]}
        ],
        "vehicle_count": 2,
        "processing_time": 0.11
    }

@router.post("/detect/all")
async def detect_all_models_parallel(file: UploadFile = File(...)):
    """
    Detect using all YOLO models in parallel for maximum speed
    Returns combined results from all models
    """
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    start_time = time.time()
    
    # Read image data
    image_data = await file.read()
    
    # Run all detections in parallel
    results = await asyncio.gather(
        detect_intrusion_api(image_data),
        detect_people_api(image_data),
        detect_security_threats_api(image_data),
        detect_vehicle_api(image_data),
        return_exceptions=True
    )
    
    total_time = time.time() - start_time
    
    # Combine results
    combined_results = {
        "success": True,
        "message": "All YOLO models processed in parallel",
        "timestamp": time.time(),
        "total_processing_time": round(total_time, 3),
        "models_processed": 4,
        "image_info": {
            "filename": file.filename,
            "content_type": file.content_type,
            "size_bytes": len(image_data)
        },
        "results": {}
    }
    
    model_names = ["intrusion", "people", "security_threats", "vehicle"]
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            combined_results["results"][model_names[i]] = {
                "error": str(result),
                "status": "failed"
            }
        else:
            combined_results["results"][model_names[i]] = {
                **result,
                "status": "success"
            }
    
    return combined_results

@router.post("/detect/all/json")
async def detect_all_models_json(request: YOLOAllRequest):
    """
    Detect using all YOLO models with JSON input (base64 image)
    """
    start_time = time.time()
    
    # Run selected models in parallel
    tasks = []
    if "intrusion" in request.include_models:
        tasks.append(detect_intrusion_api(request.image_data, request.confidence_threshold))
    if "people" in request.include_models:
        tasks.append(detect_people_api(request.image_data, request.confidence_threshold))
    if "security_threats" in request.include_models:
        tasks.append(detect_security_threats_api(request.image_data, request.confidence_threshold))
    if "vehicle" in request.include_models:
        tasks.append(detect_vehicle_api(request.image_data, request.confidence_threshold))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    total_time = time.time() - start_time
    
    return {
        "success": True,
        "message": f"Selected YOLO models processed in parallel",
        "total_processing_time": round(total_time, 3),
        "models_processed": len(request.include_models),
        "confidence_threshold": request.confidence_threshold,
        "results": {
            request.include_models[i]: result if not isinstance(result, Exception) else {"error": str(result)}
            for i, result in enumerate(results)
        }
    }

@router.get("/models/status")
async def get_models_status():
    """Get status of all YOLO models"""
    return {
        "available_models": ["intrusion", "people", "security_threats", "vehicle"],
        "parallel_processing": True,
        "estimated_time_per_model": {
            "intrusion": "~0.1s",
            "people": "~0.12s", 
            "security_threats": "~0.08s",
            "vehicle": "~0.11s"
        },
        "parallel_total_time": "~0.12s (fastest model determines total time)",
        "endpoints": [
            "/api/yolo/detect/all",
            "/api/yolo/detect/all/json",
            "/api/yolo/models/status"
        ]
    }
