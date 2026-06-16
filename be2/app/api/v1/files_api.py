"""
REST API for File Upload/Download Operations
HTTP endpoints for handling file uploads, image processing, and downloads
"""
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
import shutil
from datetime import datetime
import json
from PIL import Image
import base64
import io

from app.api.v1.auth_api import verify_token
from app.services.database_service import database_service
from app.services.models_service import yolo_service

router = APIRouter(prefix="/api/files", tags=["File Operations"])

# Configuration
UPLOAD_DIR = "uploads"
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Ensure upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(f"{UPLOAD_DIR}/images", exist_ok=True)
os.makedirs(f"{UPLOAD_DIR}/faces", exist_ok=True)
os.makedirs(f"{UPLOAD_DIR}/reports", exist_ok=True)

# Response Models
class FileUploadResponse(BaseModel):
    success: bool
    file_id: str
    filename: str
    file_path: str
    file_size: int
    upload_time: datetime

class ImageDetectionResponse(BaseModel):
    success: bool
    file_id: str
    detections: List[dict]
    processing_time: float
    image_info: dict

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return os.path.splitext(filename)[1].lower()

def is_valid_image(filename: str) -> bool:
    """Check if file is a valid image"""
    return get_file_extension(filename) in ALLOWED_IMAGE_EXTENSIONS

def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename to prevent conflicts"""
    file_ext = get_file_extension(original_filename)
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{file_ext}"

@router.post("/upload/image", response_model=FileUploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    current_user: dict = Depends(verify_token)
):
    """
    Upload image file for processing
    Supports common image formats: JPG, PNG, BMP, TIFF
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        if not is_valid_image(file.filename):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid file format. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
            )
        
        # Check file size
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        if file_size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE // 1024 // 1024}MB"
            )
        
        # Generate unique filename
        unique_filename = generate_unique_filename(file.filename)
        file_path = os.path.join(UPLOAD_DIR, "images", unique_filename)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Generate file ID
        file_id = str(uuid.uuid4())
        
        # Save file info to database
        insert_query = """
            INSERT INTO uploaded_files (file_id, original_name, stored_name, file_path, 
                                      file_size, file_type, uploaded_by, upload_time, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        await database_service.execute_query(insert_query, {
            "file_id": file_id,
            "original_name": file.filename,
            "stored_name": unique_filename,
            "file_path": file_path,
            "file_size": file_size,
            "file_type": "image",
            "uploaded_by": current_user["user_id"],
            "upload_time": datetime.now(),
            "description": description
        })
        
        return FileUploadResponse(
            success=True,
            file_id=file_id,
            filename=file.filename,
            file_path=file_path,
            file_size=file_size,
            upload_time=datetime.now()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload image: {str(e)}"
        )

@router.post("/upload/face")
async def upload_face_data(
    file: UploadFile = File(...),
    person_name: str = Form(...),
    person_id: Optional[str] = Form(None),
    department: Optional[str] = Form(None),
    current_user: dict = Depends(verify_token)
):
    """
    Upload face image for recognition system
    """
    try:
        # Validate image
        if not is_valid_image(file.filename):
            raise HTTPException(
                status_code=400,
                detail="Invalid image format for face data"
            )
        
        # Read file content
        content = await file.read()
        
        # Generate unique filename
        unique_filename = generate_unique_filename(f"{person_name}_{file.filename}")
        file_path = os.path.join(UPLOAD_DIR, "faces", unique_filename)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Save face data to database
        face_id = str(uuid.uuid4())
        insert_query = """
            INSERT INTO face_data (face_id, person_name, person_id, department, 
                                 image_path, uploaded_by, upload_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        await database_service.execute_query(insert_query, {
            "face_id": face_id,
            "person_name": person_name,
            "person_id": person_id,
            "department": department,
            "image_path": file_path,
            "uploaded_by": current_user["user_id"],
            "upload_time": datetime.now()
        })
        
        return {
            "success": True,
            "face_id": face_id,
            "person_name": person_name,
            "message": "Face data uploaded successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload face data: {str(e)}"
        )

@router.post("/detect/upload", response_model=ImageDetectionResponse)
async def detect_objects_from_upload(
    file: UploadFile = File(...),
    model_type: str = Form("intrusion"),
    confidence: float = Form(0.5),
    current_user: dict = Depends(verify_token)
):
    """
    Upload image and run object detection
    """
    try:
        # Validate image
        if not is_valid_image(file.filename):
            raise HTTPException(
                status_code=400,
                detail="Invalid image format"
            )
        
        # Read and validate file
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="File too large"
            )
        
        # Convert to base64 for YOLO service
        image_base64 = base64.b64encode(content).decode('utf-8')
        
        # Run detection
        detection_result = await yolo_service.detect_objects(
            model_type=model_type,
            image_data=image_base64,
            confidence=confidence
        )
        
        # Save detection result
        file_id = str(uuid.uuid4())
        
        # Save file temporarily for record keeping
        unique_filename = generate_unique_filename(file.filename)
        file_path = os.path.join(UPLOAD_DIR, "images", unique_filename)
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Get image info
        with Image.open(io.BytesIO(content)) as img:
            image_info = {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "mode": img.mode
            }
        
        # Save detection record
        insert_query = """
            INSERT INTO detection_results (result_id, file_id, model_type, 
                                         detections_json, processing_time, 
                                         confidence_threshold, performed_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        await database_service.execute_query(insert_query, {
            "result_id": str(uuid.uuid4()),
            "file_id": file_id,
            "model_type": model_type,
            "detections_json": json.dumps(detection_result.get("detections", [])),
            "processing_time": detection_result.get("processing_time", 0),
            "confidence_threshold": confidence,
            "performed_by": current_user["user_id"],
            "created_at": datetime.now()
        })
        
        return ImageDetectionResponse(
            success=detection_result.get("success", True),
            file_id=file_id,
            detections=detection_result.get("detections", []),
            processing_time=detection_result.get("processing_time", 0),
            image_info=image_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Detection failed: {str(e)}"
        )

@router.get("/download/{file_id}")
async def download_file(
    file_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    Download file by file ID
    """
    try:
        # Get file info from database
        query = """
            SELECT original_name, stored_name, file_path, file_type
            FROM uploaded_files 
            WHERE file_id = ?
        """
        file_info = await database_service.fetch_one(query, {"file_id": file_id})
        
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found")
        
        file_path = file_info["file_path"]
        
        # Check if file exists
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found on disk")
        
        return FileResponse(
            path=file_path,
            filename=file_info["original_name"],
            media_type="application/octet-stream"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to download file: {str(e)}"
        )

@router.get("/list")
async def list_uploaded_files(
    file_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(verify_token)
):
    """
    List uploaded files with pagination
    """
    try:
        conditions = []
        params = {}
        
        base_query = """
            SELECT file_id, original_name, file_size, file_type, 
                   upload_time, description
            FROM uploaded_files
        """
        
        if file_type:
            conditions.append("file_type = ?")
            params["file_type"] = file_type
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
        
        base_query += " ORDER BY upload_time DESC LIMIT ? OFFSET ?"
        params["limit"] = limit
        params["offset"] = offset
        
        files = await database_service.fetch_all(base_query, params)
        
        return {
            "success": True,
            "files": [
                {
                    "file_id": f["file_id"],
                    "filename": f["original_name"],
                    "file_size": f["file_size"],
                    "file_type": f["file_type"],
                    "upload_time": f["upload_time"],
                    "description": f.get("description")
                }
                for f in files
            ],
            "total_count": len(files),
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list files: {str(e)}"
        )

@router.delete("/delete/{file_id}")
async def delete_file(
    file_id: str,
    current_user: dict = Depends(verify_token)
):
    """
    Delete uploaded file
    """
    try:
        # Check if user is admin or file owner
        file_query = """
            SELECT file_path, uploaded_by 
            FROM uploaded_files 
            WHERE file_id = ?
        """
        file_info = await database_service.fetch_one(file_query, {"file_id": file_id})
        
        if not file_info:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check permissions
        user_query = "SELECT role FROM users WHERE username = ?"
        user_info = await database_service.fetch_one(user_query, {"username": current_user["sub"]})
        
        if (user_info.get("role") != "admin" and 
            file_info["uploaded_by"] != current_user["user_id"]):
            raise HTTPException(
                status_code=403,
                detail="Permission denied. Can only delete own files or admin required."
            )
        
        # Delete file from disk
        file_path = file_info["file_path"]
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete from database
        delete_query = "DELETE FROM uploaded_files WHERE file_id = ?"
        await database_service.execute_query(delete_query, {"file_id": file_id})
        
        return {
            "success": True,
            "message": "File deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete file: {str(e)}"
        )

@router.post("/generate-report")
async def generate_report(
    report_type: str = Form(...),
    start_date: Optional[str] = Form(None),
    end_date: Optional[str] = Form(None),
    filters: Optional[str] = Form(None),
    current_user: dict = Depends(verify_token)
):
    """
    Generate and download report file
    """
    try:
        # Generate report based on type
        report_data = []
        
        if report_type == "attendance":
            query = """
                SELECT u.username, a.date, a.check_in, a.check_out, a.location
                FROM users u
                LEFT JOIN attendance a ON u.id = a.user_id
            """
            conditions = []
            params = {}
            
            if start_date:
                conditions.append("a.date >= ?")
                params["start_date"] = start_date
            
            if end_date:
                conditions.append("a.date <= ?")
                params["end_date"] = end_date
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY a.date DESC"
            
            report_data = await database_service.fetch_all(query, params)
        
        elif report_type == "detections":
            query = """
                SELECT dr.model_type, dr.processing_time, dr.confidence_threshold,
                       dr.created_at, u.username as performed_by
                FROM detection_results dr
                LEFT JOIN users u ON dr.performed_by = u.id
            """
            conditions = []
            params = {}
            
            if start_date:
                conditions.append("dr.created_at >= ?")
                params["start_date"] = start_date
            
            if end_date:
                conditions.append("dr.created_at <= ?")
                params["end_date"] = end_date
            
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY dr.created_at DESC"
            
            report_data = await database_service.fetch_all(query, params)
        
        # Generate report file
        report_id = str(uuid.uuid4())
        report_filename = f"{report_type}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path = os.path.join(UPLOAD_DIR, "reports", report_filename)
        
        # Save report as JSON
        with open(report_path, "w") as f:
            json.dump({
                "report_type": report_type,
                "generated_at": datetime.now().isoformat(),
                "generated_by": current_user["sub"],
                "filters": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "additional_filters": filters
                },
                "data": [dict(row) for row in report_data]
            }, f, indent=2, default=str)
        
        # Save report record
        insert_query = """
            INSERT INTO generated_reports (report_id, report_type, file_path, 
                                         generated_by, generated_at, filters_json)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        await database_service.execute_query(insert_query, {
            "report_id": report_id,
            "report_type": report_type,
            "file_path": report_path,
            "generated_by": current_user["user_id"],
            "generated_at": datetime.now(),
            "filters_json": json.dumps({
                "start_date": start_date,
                "end_date": end_date,
                "filters": filters
            })
        })
        
        return FileResponse(
            path=report_path,
            filename=report_filename,
            media_type="application/json"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate report: {str(e)}"
        )
