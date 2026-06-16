from fastapi import APIRouter, HTTPException, Depends
from typing import List
from be2.app.services.attendance_logs_service import attendance_service
from be2.app.schemas.attendance_logs_schemas import AttendanceLogCreate, AttendanceLog, AttendanceLogUpdate

router = APIRouter()

@router.post("/", response_model=AttendanceLog)
async def create_attendance_log(data: AttendanceLogCreate):
    """Create new attendance log"""
    try:
        return await attendance_service.create_log(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[AttendanceLog])
async def get_attendance_logs():
    """Get all attendance logs"""
    try:
        return await attendance_service.get_logs()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{log_id}", response_model=AttendanceLog)
async def get_attendance_log(log_id: int):
    """Get attendance log by ID"""
    try:
        log = await attendance_service.get_log_by_id(log_id)
        if not log:
            raise HTTPException(status_code=404, detail="Attendance log not found")
        return log
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{log_id}", response_model=AttendanceLog)
async def update_attendance_log(log_id: int, data: AttendanceLogUpdate):
    """Update attendance log"""
    try:
        updated = await attendance_service.update_log(log_id, data)
        if not updated:
            raise HTTPException(status_code=404, detail="Attendance log not found")
        return updated
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{log_id}")
async def delete_attendance_log(log_id: int):
    """Delete attendance log"""
    try:
        deleted = await attendance_service.delete_log(log_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Attendance log not found")
        return {"success": True, "message": "Attendance log deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))