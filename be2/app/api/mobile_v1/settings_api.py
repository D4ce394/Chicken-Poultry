# settings_api

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from be2.app.services.settings_service import settings_service
from be2.app.schemas.settings_schemas import Setting, SettingCreate, SettingUpdate
from be2.app.models.settings import get_db  # Pastikan ada dependency get_db

router = APIRouter()

@router.post("/", response_model=Setting)
async def create_setting(data: SettingCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await settings_service.create_setting(db, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Setting])
async def get_settings(db: AsyncSession = Depends(get_db)):
    try:
        return await settings_service.get_settings(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{setting_id}", response_model=Setting)
async def get_setting(setting_id: int, db: AsyncSession = Depends(get_db)):
    try:
        setting = await settings_service.get_setting_by_id(db, setting_id)
        if not setting:
            raise HTTPException(status_code=404, detail="Setting not found")
        return setting
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{setting_id}", response_model=Setting)
async def update_setting(setting_id: int, data: SettingUpdate, db: AsyncSession = Depends(get_db)):
    try:
        updated = await settings_service.update_setting(db, setting_id, data)
        if not updated:
            raise HTTPException(status_code=404, detail="Setting not found")
        return updated
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{setting_id}")
async def delete_setting(setting_id: int, db: AsyncSession = Depends(get_db)):
    try:
        deleted = await settings_service.delete_setting(db, setting_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Setting not found")
        return {"success": True, "message": "Setting deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))