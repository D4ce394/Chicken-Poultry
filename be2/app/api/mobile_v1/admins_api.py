from fastapi import APIRouter, HTTPException
from typing import List
from be2.app.services.admins_service import admins_service
from be2.app.schemas.admins_schemas import AdminCreate, Admin, AdminUpdate

router = APIRouter()

@router.post("/", response_model=Admin)
async def create_admin(data: AdminCreate):
    """Create new admin"""
    try:
        return await admins_service.create_admin(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Admin])
async def get_admins():
    """Get all admins"""
    try:
        return await admins_service.get_admins()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{admin_id}", response_model=Admin)
async def get_admin(admin_id: int):
    """Get admin by ID"""
    try:
        admin = await admins_service.get_admin_by_id(admin_id)
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        return admin
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{admin_id}", response_model=Admin)
async def update_admin(admin_id: int, data: AdminUpdate):
    """Update admin"""
    try:
        updated = await admins_service.update_admin(admin_id, data)
        if not updated:
            raise HTTPException(status_code=404, detail="Admin not found")
        return updated
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{admin_id}")
async def delete_admin(admin_id: int):
    """Delete admin"""
    try:
        deleted = await admins_service.delete_admin(admin_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Admin not found")
        return {"success": True, "message": "Admin deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))