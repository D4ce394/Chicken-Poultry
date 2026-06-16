# notification_logs_schemas

from pydantic import BaseModel
from typing import Optional

class NotificationLogBase(BaseModel):
    user_id: int
    email_sent: Optional[bool] = False
    message: Optional[str] = None

class NotificationLogCreate(NotificationLogBase):
    pass

class NotificationLogUpdate(BaseModel):
    email_sent: Optional[bool] = None
    message: Optional[str] = None

class NotificationLog(NotificationLogBase):
    id: int

    class Config:
        orm_mode = True