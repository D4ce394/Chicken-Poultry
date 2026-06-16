"""
Mobile Authentication API
Simplified authentication endpoints for mobile applications
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.auth_service import auth_service
import jwt
import os
from datetime import datetime, timedelta

router = APIRouter()

class MobileLoginRequest(BaseModel):
    username: str
    password: str

class MobileSignupRequest(BaseModel):
    username: str
    password: str
    email: str = ""

@router.post("/login")
async def mobile_login(request: MobileLoginRequest):
    """Mobile login with extended token expiry"""
    try:
        result = await auth_service.authenticate_admin(request.username, request.password)
        
        # Extend token expiry for mobile (24 hours)
        if result.get("success"):
            token_data = {
                "username": request.username,
                "exp": datetime.utcnow() + timedelta(hours=24)
            }
            
            extended_token = jwt.encode(
                token_data,
                os.getenv("JWT_SECRET", "ai-frss-secret-key"),
                algorithm="HS256"
            )
            
            result["token"] = extended_token
            result["expires_in"] = "24h"
            
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mobile login failed: {str(e)}")

@router.post("/signup")
async def mobile_signup(request: MobileSignupRequest):
    """Mobile signup"""
    try:
        await auth_service.create_admin(request.username, request.password)
        return {
            "success": True,
            "message": "Mobile account created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Mobile signup failed: {str(e)}")

@router.post("/refresh")
async def mobile_refresh_token(token: str):
    """Refresh mobile token"""
    try:
        # Verify current token
        decoded = jwt.decode(
            token,
            os.getenv("JWT_SECRET", "ai-frss-secret-key"),
            algorithms=["HS256"]
        )
        
        # Create new token with extended expiry
        new_token_data = {
            "username": decoded["username"],
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        
        new_token = jwt.encode(
            new_token_data,
            os.getenv("JWT_SECRET", "ai-frss-secret-key"),
            algorithm="HS256"
        )
        
        return {
            "success": True,
            "token": new_token,
            "expires_in": "24h"
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))