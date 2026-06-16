from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DeviceBase(BaseModel):
    device_name: str
    device_token: Optional[str] = None
    location: Optional[str] = None
    status: Optional[int] = 1
    last_sync: Optional[datetime] = None

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(BaseModel):
    device_name: Optional[str] = None
    device_token: Optional[str] = None
    location: Optional[str] = None
    status: Optional[int] = None
    last_sync: Optional[datetime] = None

class Device(DeviceBase):
    device_id: int
    created_at: datetime

    class Config:
        orm_mode = True