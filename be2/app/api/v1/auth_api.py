"""
REST API for Authentication
HTTP endpoints for login, register, and token management
"""
from fastapi import APIRouter, HTTPException, Depends, status, Form, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
import jwt
import bcrypt
from datetime import datetime, timedelta
from app.services.database_service import database_service

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
security = HTTPBearer()

# Request/Response Models
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "user"

class LoginResponse(BaseModel):
    success: bool
    token: str
    user: dict
    expires_in: int

class RefreshRequest(BaseModel):
    refresh_token: str

# JWT Configuration
JWT_SECRET = "your-secret-key-here"  # Should be in environment variables
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token"""
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    User login endpoint
    Returns JWT token for authenticated requests
    """
    try:
        # Query user from database
        query = "SELECT * FROM users WHERE username = ?"
        user_result = await database_service.fetch_one(query, {"username": request.username})
        
        if not user_result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Verify password (assuming bcrypt hashing)
        if not bcrypt.checkpw(request.password.encode('utf-8'), user_result['password'].encode('utf-8')):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_result["username"], "user_id": user_result["id"]},
            expires_delta=access_token_expires
        )
        
        # Update last login
        update_query = "UPDATE users SET last_login = ? WHERE id = ?"
        await database_service.execute_query(update_query, {
            "last_login": datetime.now(),
            "user_id": user_result["id"]
        })
        
        return LoginResponse(
            success=True,
            token=access_token,
            user={
                "id": user_result["id"],
                "username": user_result["username"],
                "email": user_result.get("email"),
                "role": user_result.get("role", "user")
            },
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.post("/register")
async def register(request: RegisterRequest):
    """
    User registration endpoint
    Creates new user account
    """
    try:
        # Check if user already exists
        check_query = "SELECT id FROM users WHERE username = ? OR email = ?"
        existing_user = await database_service.fetch_one(check_query, {
            "username": request.username,
            "email": request.email
        })
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )
        
        # Hash password
        hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt())
        
        # Insert new user
        insert_query = """
            INSERT INTO users (username, email, password, role, created_at, is_approved)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        await database_service.execute_query(insert_query, {
            "username": request.username,
            "email": request.email,
            "password": hashed_password.decode('utf-8'),
            "role": request.role,
            "created_at": datetime.now(),
            "is_approved": False  # Requires admin approval
        })
        
        return {
            "success": True,
            "message": "User registered successfully. Waiting for admin approval.",
            "username": request.username
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/refresh")
async def refresh_token(request: RefreshRequest):
    """
    Refresh access token
    """
    try:
        # Verify refresh token
        payload = jwt.decode(request.refresh_token, JWT_SECRET, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": username},
            expires_delta=access_token_expires
        )
        
        return {
            "success": True,
            "access_token": access_token,
            "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

@router.get("/me")
async def get_current_user(current_user: dict = Depends(verify_token)):
    """
    Get current user profile
    """
    try:
        query = "SELECT id, username, email, role, created_at, last_login FROM users WHERE username = ?"
        user = await database_service.fetch_one(query, {"username": current_user["sub"]})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return {
            "success": True,
            "user": dict(user)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )

@router.post("/logout")
async def logout(current_user: dict = Depends(verify_token)):
    """
    User logout
    In a production app, you might want to blacklist the token
    """
    return {
        "success": True,
        "message": "Logged out successfully"
    }

@router.post("/change-password")
async def change_password(
    old_password: str = Form(...),
    new_password: str = Form(...),
    current_user: dict = Depends(verify_token)
):
    """
    Change user password
    """
    try:
        # Get current password
        query = "SELECT password FROM users WHERE username = ?"
        user = await database_service.fetch_one(query, {"username": current_user["sub"]})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify old password
        if not bcrypt.checkpw(old_password.encode('utf-8'), user['password'].encode('utf-8')):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Hash new password
        new_hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        # Update password
        update_query = "UPDATE users SET password = ?, updated_at = ? WHERE username = ?"
        await database_service.execute_query(update_query, {
            "password": new_hashed.decode('utf-8'),
            "updated_at": datetime.now(),
            "username": current_user["sub"]
        })
        
        return {
            "success": True,
            "message": "Password changed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to change password: {str(e)}"
        )
