from pydantic import BaseModel, validator
from typing import Optional

class AdminSignUp(BaseModel):
    username: str
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if len(v) > 50:
            raise ValueError('Username must be less than 50 characters')
        return v.strip()
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

class AdminLogin(BaseModel):
    username: str
    password: str
    
    @validator('username')
    def validate_username(cls, v):
        return v.strip()

class AdminResponse(BaseModel):
 type: str
 success: bool
 message: str
 token: Optional[str] = None
 admin: Optional[dict] = None
