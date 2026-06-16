"""
CCTV/IP Camera API
Handles IP camera management and monitoring
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional

from app.services.cctv_service import cctv_service
from app.schemas.video_schemas import (
    AddCameraRequest, CameraInfo, CameraListResponse,
    SystemStatusResponse, DetectionHistoryResponse, CameraConfig
)

router = APIRouter()

@router.post("/cameras", response_model=CameraInfo)
async def add_camera(request: AddCameraRequest):
    """
    Add new IP camera to monitoring system
    
    **Example URLs:**
    - RTSP: `rtsp://admin:password@192.168.1.100:554/stream`
    - HTTP: `http://192.168.1.100:8080/video`
    - USB Camera: `0` (for local USB camera)
    """
    try:
        camera_id = cctv_service.add_camera(
            stream_url=request.stream_url,
            name=request.name,
        )
        
        # Update configuration if provided
        if request.config:
            cctv_service.update_camera_config(camera_id, request.config.dict())
        
        camera = cctv_service.get_camera(camera_id)
        return CameraInfo(**camera.get_info())
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add camera: {str(e)}")

@router.get("/cameras", response_model=CameraListResponse)
async def list_cameras():
    """
    List all registered cameras
    """
    try:
        cameras = cctv_service.list_cameras()
        return CameraListResponse(
            cameras=[CameraInfo(**cam) for cam in cameras],
            total_count=len(cameras)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cameras/{camera_id}", response_model=CameraInfo)
async def get_camera(camera_id: str):
    """
    Get specific camera information
    
    - **camera_id**: Camera ID to retrieve
    """
    try:
        camera = cctv_service.get_camera(camera_id)
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")
        
        return CameraInfo(**camera.get_info())
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/cameras/{camera_id}/config")
async def update_camera_config(camera_id: str, config: CameraConfig):
    """
    Update camera configuration
    
    - **camera_id**: Camera ID to update
    - **config**: New configuration parameters
    """
    try:
        success = cctv_service.update_camera_config(camera_id, config.dict())
        if not success:
            raise HTTPException(status_code=404, detail="Camera not found")
        
        return {"message": "Camera configuration updated"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cameras/{camera_id}/start")
async def start_camera_monitoring(camera_id: str, background_tasks: BackgroundTasks):
    """
    Start monitoring specific camera
    
    - **camera_id**: Camera ID to start monitoring
    """
    try:
        success = await cctv_service.start_camera_monitoring(camera_id)
        if not success:
            raise HTTPException(status_code=400, detail="Failed to start camera monitoring")
        
        return {"message": f"Camera {camera_id} monitoring started"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/cameras/{camera_id}/stop")
async def stop_camera_monitoring(camera_id: str):
    """
    Stop monitoring specific camera
    
    - **camera_id**: Camera ID to stop monitoring
    """
    try:
        cctv_service.stop_camera_monitoring(camera_id)
        return {"message": f"Camera {camera_id} monitoring stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/cameras/{camera_id}")
async def remove_camera(camera_id: str):
    """
    Remove camera from system
    
    - **camera_id**: Camera ID to remove
    """
    try:
        success = cctv_service.remove_camera(camera_id)
        if not success:
            raise HTTPException(status_code=404, detail="Camera not found")
        
        return {"message": f"Camera {camera_id} removed"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/monitoring/start")
async def start_all_monitoring(background_tasks: BackgroundTasks):
    """
    Start monitoring all cameras
    """
    try:
        background_tasks.add_task(cctv_service.start_all_monitoring)
        return {"message": "All camera monitoring started"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/monitoring/stop")
async def stop_all_monitoring():
    """
    Stop monitoring all cameras
    """
    try:
        cctv_service.stop_all_monitoring()
        return {"message": "All camera monitoring stopped"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/monitoring/status", response_model=SystemStatusResponse)
async def get_system_status():
    """
    Get overall monitoring system status
    """
    try:
        status = cctv_service.get_system_status()
        return SystemStatusResponse(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/detections/history", response_model=DetectionHistoryResponse)
async def get_detection_history(
    camera_id: Optional[str] = None,
    limit: int = 50
):
    """
    Get detection history
    
    - **camera_id**: Optional camera ID to filter by
    - **limit**: Maximum number of events to return
    """
    try:
        events = cctv_service.get_detection_history(camera_id, limit)
        return DetectionHistoryResponse(
            events=events,
            total_count=len(events),
            camera_id=camera_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cameras/{camera_id}/live-frame")
async def get_live_frame(camera_id: str):
    """
    Get latest frame from camera
    
    - **camera_id**: Camera ID to get frame from
    """
    try:
        camera = cctv_service.get_camera(camera_id)
        if not camera:
            raise HTTPException(status_code=404, detail="Camera not found")
        
        if not camera.is_active:
            raise HTTPException(status_code=400, detail="Camera is not active")
        
        frame_data = camera.capture_frame()
        if not frame_data:
            raise HTTPException(status_code=500, detail="Failed to capture frame")
        
        return {
            "camera_id": camera_id,
            "timestamp": camera.stats.get("last_frame_time"),
            "frame_data": frame_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
