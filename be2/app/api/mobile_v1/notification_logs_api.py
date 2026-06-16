# notification_logs_api

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from be2.app.services.notification_logs_service import notification_logs_service
from be2.app.schemas.notification_logs_schemas import (
    NotificationLog,
    NotificationLogCreate,
    NotificationLogUpdate,
)
from be2.app.models.notification_logs import get_db  # Pastikan ada dependency get_db

router = APIRouter()

@router.post("/", response_model=NotificationLog)
async def create_notification_log(
    data: NotificationLogCreate, db: AsyncSession = Depends(get_db)
):
    try:
        return await notification_logs_service.create_log(db, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[NotificationLog])
async def get_notification_logs(db: AsyncSession = Depends(get_db)):
    try:
        return await notification_logs_service.get_logs(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{log_id}", response_model=NotificationLog)
async def get_notification_log(log_id: int, db: AsyncSession = Depends(get_db)):
    try:
        log = await notification_logs_service.get_log_by_id(db, log_id)
        if not log:
            raise HTTPException(status_code=404, detail="Notification log not found")
        return log
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{log_id}", response_model=NotificationLog)
async def update_notification_log(
    log_id: int, data: NotificationLogUpdate, db: AsyncSession = Depends(get_db)
):
    try:
        updated = await notification_logs_service.update_log(db, log_id, data)
        if not updated:
            raise HTTPException(status_code=404, detail="Notification log not found")
        return updated
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{log_id}")
async def delete_notification_log(log_id: int, db: AsyncSession = Depends(get_db)):
    try:
        deleted = await notification_logs_service.delete_log(db, log_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Notification log not found")
        return {"success": True, "message": "Notification log deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))