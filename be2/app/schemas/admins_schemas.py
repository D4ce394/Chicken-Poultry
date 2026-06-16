from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class AdminBase(BaseModel):
    username: str
    email: EmailStr

class AdminCreate(AdminBase):
    password: str

class AdminUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class Admin(AdminBase):
    id: int
    created_at: datetime
    is_active: bool
    password: str  # For demo only; in production, don't expose password!

    class Config:
        orm_mode = True