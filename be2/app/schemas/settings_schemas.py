# settings_schemas

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SettingBase(BaseModel):
    key: str
    value: str

class SettingCreate(SettingBase):
    pass

class SettingUpdate(BaseModel):
    key: Optional[str] = None
    value: Optional[str] = None

class Setting(SettingBase):
    setting_id: int
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True