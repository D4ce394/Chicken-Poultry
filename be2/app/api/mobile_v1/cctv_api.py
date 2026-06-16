"""
Mobile CCTV Integration API
CCTV camera management and live feed endpoints optimized for mobile
"""
from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import List, Optional
import json

# Mock CCTV service for mobile (implement based on actual cctv_service)
router = APIRouter()

class MobileCameraInfo(BaseModel):
    id: str
    name: str
    location: str
    status: str
    last_snapshot: Optional[str] = None

@router.get("/cameras")
async def list_mobile_cameras():
    """Get list of CCTV cameras optimized for mobile display"""
    try:
        # Mock data - replace with actual cctv_service integration
        cameras = [
            {
                "id": "cam_001",
                "name": "Front Gate",
                "location": "Main Entrance",
                "status": "online",
                "last_snapshot": "2025-08-12T10:30:00"
            },
            {
                "id": "cam_002", 
                "name": "Parking Lot",
                "location": "Building A",
                "status": "offline",
                "last_snapshot": "2025-08-12T09:15:00"
            }
        ]
        
        return {
            "success": True,
            "cameras": cameras,
            "total": len(cameras),
            "online_count": len([c for c in cameras if c["status"] == "online"])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cameras: {str(e)}")

@router.get("/cameras/{camera_id}/snapshot")
async def get_mobile_camera_snapshot(camera_id: str):
    """Get camera snapshot optimized for mobile (compressed)"""
    try:
        # Mock implementation - replace with actual camera integration
        return {
            "success": True,
            "camera_id": camera_id,
            "image_base64": "mock_base64_compressed_image_data",
            "timestamp": "2025-08-12T10:30:00",
            "resolution": "640x480",  # Mobile-optimized resolution
            "compression": "85%"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get snapshot: {str(e)}")

@router.post("/cameras/{camera_id}/detect")
async def mobile_camera_detect(camera_id: str, model_type: str = "intrusion"):
    """Run AI detection on camera feed for mobile"""
    try:
        # Get camera snapshot first (mobile optimized)
        # Then run YOLO detection
        
        from app.services.models_service import yolo_service
        
        # Mock image data - replace with actual camera snapshot
        mock_image = "mock_base64_image_data"
        
        result = await yolo_service.detect_objects(
            model_type=model_type,
            image_data=mock_image,
            confidence=0.5
        )
        
        # Mobile-optimized response
        mobile_detections = []
        for detection in result.get("detections", []):
            mobile_detections.append({
                "type": detection.get("class_name", "unknown"),
                "confidence": f"{detection.get('confidence', 0)*100:.0f}%",
                "position": detection.get("bbox", [])
            })
        
        return {
            "success": True,
            "camera_id": camera_id,
            "camera_name": f"Camera {camera_id}",
            "model_used": model_type,
            "objects_found": mobile_detections,
            "total_objects": len(mobile_detections),
            "processing_time": f"{result.get('processing_time', 0):.2f}s",
            "timestamp": "2025-08-12T10:30:00"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

@router.websocket("/live/{camera_id}")
async def mobile_live_feed(websocket: WebSocket, camera_id: str):
    """Mobile WebSocket live camera feed with detection"""
    await websocket.accept()
    
    try:
        await websocket.send_text(json.dumps({
            "type": "connected",
            "camera_id": camera_id,
            "message": "Mobile live feed connected"
        }))
        
        while True:
            try:
                message = await websocket.receive_text()
                data = json.loads(message)
                
                if data.get("type") == "start_detection":
                    # Start live detection on camera feed
                    await websocket.send_text(json.dumps({
                        "type": "detection_started",
                        "model": data.get("model", "intrusion")
                    }))
                    
                elif data.get("type") == "get_snapshot":
                    # Send current frame
                    await websocket.send_text(json.dumps({
                        "type": "snapshot",
                        "image_base64": "mock_mobile_optimized_frame",
                        "timestamp": "2025-08-12T10:30:00"
                    }))
                    
                elif data.get("type") == "stop":
                    break
                    
            except WebSocketDisconnect:
                break
                
    except Exception as e:
        await websocket.send_text(json.dumps({
            "type": "error", 
            "message": str(e)
        }))
    finally:
        # Cleanup mobile streaming resources
        pass

@router.get("/status")
async def get_mobile_cctv_status():
    """Get CCTV system status for mobile dashboard"""
    try:
        return {
            "success": True,
            "system_status": "operational",
            "total_cameras": 5,
            "online_cameras": 3,
            "offline_cameras": 2,
            "active_detections": 12,
            "last_alert": "2025-08-12T10:25:00",
            "uptime": "99.5%"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
