"""
Mobile API Router
Consolidated API endpoints specifically designed for mobile applications
Simplified responses and optimized for mobile data usage
"""
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import base64
import json
from datetime import datetime

from app.api.v1.auth_api import verify_token, create_access_token
from app.services.database_service import database_service
from app.services.models_service import yolo_service

router = APIRouter(prefix="/api/mobile", tags=["Mobile API"])

# Mobile-optimized request/response models
class MobileLoginRequest(BaseModel):
    username: str
    password: str

class MobileLoginResponse(BaseModel):
    success: bool
    token: str
    user: Dict[str, Any]
    server_time: str

class MobileDetectionRequest(BaseModel):
    image_base64: str
    model_type: str = "intrusion"
    confidence: float = 0.5

class MobileDetectionResponse(BaseModel):
    success: bool
    detections: List[Dict[str, Any]]
    processing_time: float
    total_objects: int

class MobileUserProfile(BaseModel):
    id: int
    username: str
    email: str
    role: str
    department: Optional[str]
    last_login: Optional[str]

@router.post("/auth/login", response_model=MobileLoginResponse)
async def mobile_login(request: MobileLoginRequest):
    """
    Mobile app login - optimized response
    """
    try:
        # Query user from database
        query = "SELECT * FROM users WHERE username = ? AND is_approved = ?"
        user_result = await database_service.fetch_one(query, {
            "username": request.username,
            "is_approved": True
        })
        
        if not user_result:
            raise HTTPException(status_code=401, detail="Invalid credentials or account not approved")
        
        # Verify password
        import bcrypt
        if not bcrypt.checkpw(request.password.encode('utf-8'), user_result['password'].encode('utf-8')):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Create token
        from datetime import timedelta
        access_token = create_access_token(
            data={"sub": user_result["username"], "user_id": user_result["id"]},
            expires_delta=timedelta(hours=24)  # Longer expiry for mobile
        )
        
        # Update last login
        update_query = "UPDATE users SET last_login = ?, is_online = ? WHERE id = ?"
        await database_service.execute_query(update_query, {
            "last_login": datetime.now(),
            "is_online": True,
            "user_id": user_result["id"]
        })
        
        return MobileLoginResponse(
            success=True,
            token=access_token,
            user={
                "id": user_result["id"],
                "username": user_result["username"],
                "email": user_result.get("email", ""),
                "role": user_result.get("role", "user"),
                "department": user_result.get("department", "")
            },
            server_time=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")

@router.get("/profile", response_model=MobileUserProfile)
async def get_mobile_profile(current_user: dict = Depends(verify_token)):
    """
    Get user profile for mobile app
    """
    try:
        query = """
            SELECT id, username, email, role, department, last_login
            FROM users WHERE username = ?
        """
        user = await database_service.fetch_one(query, {"username": current_user["sub"]})
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return MobileUserProfile(
            id=user["id"],
            username=user["username"],
            email=user.get("email", ""),
            role=user.get("role", "user"),
            department=user.get("department"),
            last_login=user.get("last_login").isoformat() if user.get("last_login") else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/detect", response_model=MobileDetectionResponse)
async def mobile_detection(request: MobileDetectionRequest, current_user: dict = Depends(verify_token)):
    """
    Mobile object detection - optimized for mobile usage
    """
    try:
        # Validate model type
        valid_models = ["intrusion", "people", "security_threats", "vehicle"]
        if request.model_type not in valid_models:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid model type. Use one of: {', '.join(valid_models)}"
            )
        
        # Run detection
        detection_result = await yolo_service.detect_objects(
            model_type=request.model_type,
            image_data=request.image_base64,
            confidence=request.confidence
        )
        
        # Simplify response for mobile
        detections = detection_result.get("detections", [])
        mobile_detections = []
        
        for detection in detections:
            mobile_detections.append({
                "class": detection.get("class_name", "unknown"),
                "confidence": round(detection.get("confidence", 0), 2),
                "bbox": detection.get("bbox", []),
                "center": detection.get("center", [])
            })
        
        # Save detection record (optional)
        try:
            insert_query = """
                INSERT INTO mobile_detections (user_id, model_type, detection_count, 
                                             processing_time, created_at)
                VALUES (?, ?, ?, ?, ?)
            """
            await database_service.execute_query(insert_query, {
                "user_id": current_user["user_id"],
                "model_type": request.model_type,
                "detection_count": len(mobile_detections),
                "processing_time": detection_result.get("processing_time", 0),
                "created_at": datetime.now()
            })
        except Exception:
            # Silent fail for database logging
            pass
        
        return MobileDetectionResponse(
            success=True,
            detections=mobile_detections,
            processing_time=round(detection_result.get("processing_time", 0), 3),
            total_objects=len(mobile_detections)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")

@router.post("/detect/upload")
async def mobile_detection_upload(
    file: UploadFile = File(...),
    model_type: str = Form("intrusion"),
    confidence: float = Form(0.5),
    current_user: dict = Depends(verify_token)
):
    """
    Mobile detection via file upload
    """
    try:
        # Validate file
        if not file.filename or not file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
            raise HTTPException(status_code=400, detail="Invalid image file")
        
        # Read and convert to base64
        content = await file.read()
        if len(content) > 5 * 1024 * 1024:  # 5MB limit for mobile
            raise HTTPException(status_code=400, detail="File too large (max 5MB)")
        
        image_base64 = base64.b64encode(content).decode('utf-8')
        
        # Use existing detection endpoint
        detection_request = MobileDetectionRequest(
            image_base64=image_base64,
            model_type=model_type,
            confidence=confidence
        )
        
        return await mobile_detection(detection_request, current_user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/models")
async def get_available_models(current_user: dict = Depends(verify_token)):
    """
    Get available YOLO models for mobile app
    """
    try:
        models_info = await yolo_service.list_all_models()
        
        # Simplify for mobile
        mobile_models = []
        if models_info.get("success"):
            for model in models_info.get("models", []):
                mobile_models.append({
                    "type": model.get("model_type"),
                    "name": model.get("model_type").replace("_", " ").title(),
                    "classes": model.get("classes", []),
                    "loaded": model.get("loaded", False)
                })
        
        return {
            "success": True,
            "models": mobile_models,
            "total": len(mobile_models)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def get_mobile_stats(current_user: dict = Depends(verify_token)):
    """
    Get user statistics for mobile dashboard
    """
    try:
        # Get user's detection history
        history_query = """
            SELECT COUNT(*) as total_detections,
                   AVG(processing_time) as avg_processing_time,
                   MAX(created_at) as last_detection
            FROM mobile_detections 
            WHERE user_id = ?
        """
        stats = await database_service.fetch_one(history_query, {"user_id": current_user["user_id"]})
        
        # Get recent activity
        recent_query = """
            SELECT model_type, detection_count, created_at
            FROM mobile_detections 
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 5
        """
        recent_activity = await database_service.fetch_all(recent_query, {"user_id": current_user["user_id"]})
        
        return {
            "success": True,
            "stats": {
                "total_detections": stats.get("total_detections", 0) if stats else 0,
                "avg_processing_time": round(stats.get("avg_processing_time", 0), 3) if stats else 0,
                "last_detection": stats.get("last_detection") if stats else None
            },
            "recent_activity": [
                {
                    "model": activity["model_type"],
                    "objects_found": activity["detection_count"],
                    "timestamp": activity["created_at"]
                }
                for activity in recent_activity
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logout")
async def mobile_logout(current_user: dict = Depends(verify_token)):
    """
    Mobile logout - update online status
    """
    try:
        # Update online status
        update_query = "UPDATE users SET is_online = ? WHERE username = ?"
        await database_service.execute_query(update_query, {
            "is_online": False,
            "username": current_user["sub"]
        })
        
        return {
            "success": True,
            "message": "Logged out successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def mobile_health_check():
    """
    Mobile health check - lightweight status
    """
    try:
        # Quick database check
        db_status = True
        try:
            await database_service.fetch_one("SELECT 1", {})
        except:
            db_status = False
        
        # Quick YOLO check
        yolo_status = len(yolo_service.models) > 0
        
        return {
            "success": True,
            "status": "healthy" if (db_status and yolo_status) else "degraded",
            "services": {
                "database": db_status,
                "yolo": yolo_status,
                "models_loaded": len(yolo_service.models)
            },
            "server_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e),
            "server_time": datetime.now().isoformat()
        }
