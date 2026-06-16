from fastapi import APIRouter, HTTPException
from app.services.auth_service import auth_service
from app.schemas.auth_schemas import AdminSignUp, AdminLogin

router = APIRouter()

@router.post("/signup")
async def signup(data: AdminSignUp):
    """Register new admin"""
    try:
        await auth_service.create_admin(data.username, data.password)
        return {
            "type": "insert_admin",
            "success": True,
            "message": "Admin registered successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
async def login(data: AdminLogin):
    """Admin login"""
    return await auth_service.authenticate_admin(data.username, data.password)
