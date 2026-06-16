from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from be2.app.services.devices_service import devices_service
from be2.app.schemas.devices_schemas import Device, DeviceCreate, DeviceUpdate
from be2.app.models.devices import get_db  # Pastikan ada dependency get_db

router = APIRouter()

@router.post("/", response_model=Device)
async def create_device(data: DeviceCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await devices_service.create_device(db, data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Device])
async def get_devices(db: AsyncSession = Depends(get_db)):
    try:
        return await devices_service.get_devices(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{device_id}", response_model=Device)
async def get_device(device_id: int, db: AsyncSession = Depends(get_db)):
    try:
        device = await devices_service.get_device_by_id(db, device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        return device
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{device_id}", response_model=Device)
async def update_device(device_id: int, data: DeviceUpdate, db: AsyncSession = Depends(get_db)):
    try:
        updated = await devices_service.update_device(db, device_id, data)
        if not updated:
            raise HTTPException(status_code=404, detail="Device not found")
        return updated
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{device_id}")
async def delete_device(device_id: int, db: AsyncSession = Depends(get_db)):
    try:
        deleted = await devices_service.delete_device(db, device_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Device not found")
        return {"success": True, "message": "Device deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))