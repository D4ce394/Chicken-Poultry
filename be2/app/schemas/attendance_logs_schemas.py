from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AttendanceLogBase(BaseModel):
    user_id: int
    timestamp: datetime
    status: str
    note: Optional[str] = None

class AttendanceLogCreate(AttendanceLogBase):
    pass

class AttendanceLogUpdate(BaseModel):
    status: Optional[str] = None
    note: Optional[str] = None

class AttendanceLog(AttendanceLogBase):
    id: int

    class Config:
        orm_mode = True