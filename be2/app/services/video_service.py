"""
Video Processing Service
Handles video upload, frame extraction, and batch processing
"""
import os
try:
    import cv2
except Exception:
    cv2 = None
import uuid
import asyncio
import tempfile
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, UploadFile
import logging
from io import BytesIO
import base64
from PIL import Image
import json
from datetime import datetime, timedelta

from app.services.models_service import yolo_service

logger = logging.getLogger(__name__)

class VideoProcessingService:
    """Service for video upload and processing"""
    
    def __init__(self):
        self.upload_dir = "uploads/videos"
        self.processed_dir = "uploads/processed"
        self.temp_dir = "uploads/temp"
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.supported_formats = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        
        # Create directories
        for directory in [self.upload_dir, self.processed_dir, self.temp_dir]:
            os.makedirs(directory, exist_ok=True)
    
    async def upload_and_process_video(
        self, 
        video_file: UploadFile,
        model_types: List[str],
        confidence: float = 0.5,
        iou_threshold: float = 0.45,
        frame_skip: int = 30  # Process every 30th frame (1 per second for 30fps video)
    ) -> Dict[str, Any]:
        """
        Upload and process video file
        
        Args:
            video_file: Uploaded video file
            model_types: List of models to run ['intrusion', 'people', etc.]
            confidence: Detection confidence threshold
            iou_threshold: IoU threshold for NMS
            frame_skip: Process every Nth frame to optimize performance
        
        Returns:
            Processing job information
        """
        try:
            # Validate file
            if video_file.size > self.max_file_size:
                raise HTTPException(status_code=413, detail="File too large")
            
            file_ext = os.path.splitext(video_file.filename)[1].lower()
            if file_ext not in self.supported_formats:
                raise HTTPException(status_code=400, detail="Unsupported video format")
            
            # Generate unique job ID
            job_id = str(uuid.uuid4())
            
            # Save uploaded file
            video_path = os.path.join(self.upload_dir, f"{job_id}{file_ext}")
            with open(video_path, "wb") as buffer:
                content = await video_file.read()
                buffer.write(content)
            
            # Get video metadata
            metadata = self._get_video_metadata(video_path)
            
            # Start background processing
            asyncio.create_task(
                self._process_video_background(
                    job_id, video_path, model_types, 
                    confidence, iou_threshold, frame_skip
                )
            )
            
            return {
                "job_id": job_id,
                "status": "processing",
                "filename": video_file.filename,
                "metadata": metadata,
                "estimated_completion": datetime.now() + timedelta(
                    seconds=metadata["duration_seconds"] * len(model_types) * 0.1
                )
            }
            
        except Exception as e:
            logger.error(f"Video upload failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Video processing failed: {str(e)}")
    
    def _get_video_metadata(self, video_path: str) -> Dict[str, Any]:
        """Extract video metadata"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError("Could not open video file")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duration = frame_count / fps if fps > 0 else 0
        
        cap.release()
        
        return {
            "fps": fps,
            "frame_count": frame_count,
            "width": width,
            "height": height,
            "duration_seconds": duration,
            "duration_formatted": str(timedelta(seconds=int(duration)))
        }
    
    async def _process_video_background(
        self,
        job_id: str,
        video_path: str,
        model_types: List[str],
        confidence: float,
        iou_threshold: float,
        frame_skip: int
    ):
        """Background video processing task"""
        try:
            logger.info(f"Starting video processing for job {job_id}")
            
            # Update job status
            self._update_job_status(job_id, "extracting_frames")
            
            # Extract frames
            frames = self._extract_frames(video_path, frame_skip)
            
            # Process with each model
            results = {}
            for model_type in model_types:
                logger.info(f"Processing with {model_type} model")
                self._update_job_status(job_id, f"processing_{model_type}")
                
                model_results = []
                for i, frame_data in enumerate(frames):
                    try:
                        detection_result = await yolo_service.detect_objects(
                            model_type=model_type,
                            image_data=frame_data['base64'],
                            confidence=confidence,
                            iou_threshold=iou_threshold
                        )
                        
                        model_results.append({
                            "frame_number": frame_data['frame_number'],
                            "timestamp": frame_data['timestamp'],
                            "detections": detection_result['detections'],
                            "total_detections": detection_result['total_detections']
                        })
                        
                    except Exception as e:
                        logger.error(f"Frame {i} processing failed: {str(e)}")
                        continue
                
                results[model_type] = model_results
            
            # Generate summary
            summary = self._generate_video_summary(results)
            
            # Save results
            result_path = os.path.join(self.processed_dir, f"{job_id}_results.json")
            with open(result_path, 'w') as f:
                json.dump({
                    "job_id": job_id,
                    "processed_at": datetime.now().isoformat(),
                    "summary": summary,
                    "detailed_results": results
                }, f, indent=2)
            
            # Update final status
            self._update_job_status(job_id, "completed", results=summary)
            
            # Cleanup
            os.remove(video_path)
            
            logger.info(f"Video processing completed for job {job_id}")
            
        except Exception as e:
            logger.error(f"Video processing failed for job {job_id}: {str(e)}")
            self._update_job_status(job_id, "failed", error=str(e))
    
    def _extract_frames(self, video_path: str, frame_skip: int) -> List[Dict[str, Any]]:
        """Extract frames from video"""
        frames = []
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError("Could not open video file")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_number = 0
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_number % frame_skip == 0:
                # Convert frame to base64
                _, buffer = cv2.imencode('.jpg', frame)
                frame_base64 = base64.b64encode(buffer).decode('utf-8')
                
                timestamp = frame_number / fps if fps > 0 else 0
                
                frames.append({
                    "frame_number": frame_number,
                    "timestamp": timestamp,
                    "timestamp_formatted": str(timedelta(seconds=int(timestamp))),
                    "base64": frame_base64
                })
            
            frame_number += 1
        
        cap.release()
        return frames
    
    def _generate_video_summary(self, results: Dict[str, List]) -> Dict[str, Any]:
        """Generate summary from detailed results"""
        summary = {
            "total_models_processed": len(results),
            "models": {}
        }
        
        for model_type, model_results in results.items():
            total_detections = sum(r['total_detections'] for r in model_results)
            frames_with_detections = sum(1 for r in model_results if r['total_detections'] > 0)
            
            # Get unique classes detected
            classes_detected = set()
            for result in model_results:
                for detection in result['detections']:
                    classes_detected.add(detection['class_name'])
            
            # Find peak detection periods
            peak_detections = sorted(model_results, key=lambda x: x['total_detections'], reverse=True)[:5]
            
            summary["models"][model_type] = {
                "total_detections": total_detections,
                "frames_processed": len(model_results),
                "frames_with_detections": frames_with_detections,
                "detection_rate": frames_with_detections / len(model_results) if model_results else 0,
                "classes_detected": list(classes_detected),
                "peak_detection_periods": peak_detections
            }
        
        return summary
    
    def _update_job_status(self, job_id: str, status: str, **kwargs):
        """Update job status in memory/database"""
        # In production, this would update database
        # For now, save to file
        status_file = os.path.join(self.temp_dir, f"{job_id}_status.json")
        status_data = {
            "job_id": job_id,
            "status": status,
            "updated_at": datetime.now().isoformat(),
            **kwargs
        }
        
        with open(status_file, 'w') as f:
            json.dump(status_data, f, indent=2)
    
    async def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """Get processing job status"""
        status_file = os.path.join(self.temp_dir, f"{job_id}_status.json")
        
        if not os.path.exists(status_file):
            raise HTTPException(status_code=404, detail="Job not found")
        
        with open(status_file, 'r') as f:
            return json.load(f)
    
    async def get_job_results(self, job_id: str) -> Dict[str, Any]:
        """Get completed job results"""
        result_file = os.path.join(self.processed_dir, f"{job_id}_results.json")
        
        if not os.path.exists(result_file):
            raise HTTPException(status_code=404, detail="Results not found")
        
        with open(result_file, 'r') as f:
            return json.load(f)

# Global service instance
video_service = VideoProcessingService()
