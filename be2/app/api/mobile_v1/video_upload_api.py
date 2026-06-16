"""
Video Upload API
Handles video file upload and batch processing
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List

from app.services.video_service import video_service
from app.schemas.video_schemas import VideoJobResponse, JobStatusResponse, VideoResultsResponse

router = APIRouter()

@router.post("/upload", response_model=VideoJobResponse)
async def upload_video_for_processing(
    video_file: UploadFile = File(...),
    model_types: str = Form(default="intrusion"),  # Comma-separated string
    confidence: float = Form(default=0.5),
    iou_threshold: float = Form(default=0.45),
    frame_skip: int = Form(default=30)
):
    """
    Upload video file for batch processing
    
    - **video_file**: Video file to process (MP4, AVI, MOV, MKV, WEBM)
    - **model_types**: Comma-separated model names (intrusion,people,security_threats,vehicle)
    - **confidence**: Detection confidence threshold (0.0-1.0)
    - **iou_threshold**: IoU threshold for NMS (0.0-1.0)
    - **frame_skip**: Process every Nth frame (1-300)
    """
    try:
        # Parse model types
        models = [m.strip() for m in model_types.split(",") if m.strip()]
        if not models:
            models = ["intrusion"]
        
        # Validate models
        valid_models = ['intrusion', 'people', 'security_threats', 'vehicle']
        for model in models:
            if model not in valid_models:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid model type: {model}. Valid options: {valid_models}"
                )
        
        # Process video
        result = await video_service.upload_and_process_video(
            video_file=video_file,
            model_types=models,
            confidence=confidence,
            iou_threshold=iou_threshold,
            frame_skip=frame_skip
        )
        
        return VideoJobResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Video upload failed: {str(e)}")

@router.get("/job/{job_id}/status", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """
    Get video processing job status
    
    - **job_id**: Job ID returned from upload endpoint
    """
    try:
        status = await video_service.get_job_status(job_id)
        return JobStatusResponse(**status)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/job/{job_id}/results", response_model=VideoResultsResponse)
async def get_job_results(job_id: str):
    """
    Get completed video processing results
    
    - **job_id**: Job ID returned from upload endpoint
    """
    try:
        results = await video_service.get_job_results(job_id)
        return VideoResultsResponse(**results)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/jobs")
async def list_recent_jobs(limit: int = 10):
    """
    List recent video processing jobs
    
    - **limit**: Maximum number of jobs to return
    """
    try:
        # This would be implemented with proper database
        return {"message": "Job listing not implemented yet"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
