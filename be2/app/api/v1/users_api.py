"""
REST API for User Management  
HTTP endpoints for CRUD operations on users
"""
from fastapi import APIRouter, HTTPException, Depends, Query, status, Form, File, UploadFile
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime
from app.api.v1.auth_api import verify_token
from app.services.database_service import database_service

router = APIRouter(prefix="/api/users", tags=["User Management"])

# Request/Response Models
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    department: Optional[str] = None
    is_approved: bool
    is_online: bool
    created_at: datetime
    last_login: Optional[datetime] = None

class UserCreateRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: str = "user"
    department: Optional[str] = None

class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    department: Optional[str] = None
    is_approved: Optional[bool] = None

class AttendanceReport(BaseModel):
    user_id: int
    username: str
    date: str
    check_in: Optional[datetime] = None
    check_out: Optional[datetime] = None
    location: Optional[str] = None

@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    search: Optional[str] = Query(None, description="Search by username or email"),
    role_filter: Optional[str] = Query(None, description="Filter by role"),
    status_filter: Optional[str] = Query(None, description="Filter by online status"),
    approval_filter: Optional[str] = Query(None, description="Filter by approval status"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(verify_token)
):
    """
    Get all users with optional filtering
    Requires authentication
    """
    try:
        # Build query with filters
        conditions = []
        params = {}
        
        base_query = """
            SELECT id, username, email, role, department, is_approved, 
                   is_online, created_at, last_login, updated_at
            FROM users
        """
        
        if search:
            conditions.append("(username LIKE ? OR email LIKE ?)")
            params["search1"] = f"%{search}%"
            params["search2"] = f"%{search}%"
        
        if role_filter:
            conditions.append("role = ?")
            params["role"] = role_filter
            
        if status_filter:
            if status_filter.lower() == "online":
                conditions.append("is_online = ?")
                params["is_online"] = True
            elif status_filter.lower() == "offline":
                conditions.append("is_online = ?")
                params["is_online"] = False
                
        if approval_filter:
            if approval_filter.lower() == "approved":
                conditions.append("is_approved = ?")
                params["is_approved"] = True
            elif approval_filter.lower() == "pending":
                conditions.append("is_approved = ?")
                params["is_approved"] = False
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
        
        base_query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params["limit"] = limit
        params["offset"] = offset
        
        users = await database_service.fetch_all(base_query, params)
        
        return [
            UserResponse(
                id=user["id"],
                username=user["username"],
                email=user["email"],
                role=user["role"],
                department=user.get("department"),
                is_approved=bool(user["is_approved"]),
                is_online=bool(user["is_online"]),
                created_at=user["created_at"],
                last_login=user.get("last_login")
            )
            for user in users
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch users: {str(e)}"
        )

@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: dict = Depends(verify_token)):
    """
    Get current user profile
    """
    try:
        query = """
            SELECT id, username, email, role, department, is_approved,
                   is_online, created_at, last_login, updated_at
            FROM users WHERE username = ?
        """
        user = await database_service.fetch_one(query, {"username": current_user["sub"]})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        
        return UserResponse(
            id=user["id"],
            username=user["username"],
            email=user["email"],
            role=user["role"],
            department=user.get("department"),
            is_approved=bool(user["is_approved"]),
            is_online=bool(user["is_online"]),
            created_at=user["created_at"],
            last_login=user.get("last_login")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreateRequest,
    current_user: dict = Depends(verify_token)
):
    """
    Create new user (Admin only)
    """
    try:
        # Check if current user is admin
        admin_query = "SELECT role FROM users WHERE username = ?"
        admin = await database_service.fetch_one(admin_query, {"username": current_user["sub"]})
        
        if not admin or admin["role"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        
        # Check if username/email already exists
        check_query = "SELECT id FROM users WHERE username = ? OR email = ?"
        existing = await database_service.fetch_one(check_query, {
            "username": request.username,
            "email": request.email
        })
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists"
            )
        
        # Hash password
        import bcrypt
        hashed_password = bcrypt.hashpw(request.password.encode('utf-8'), bcrypt.gensalt())
        
        # Insert user
        insert_query = """
            INSERT INTO users (username, email, password, role, department, is_approved, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        await database_service.execute_query(insert_query, {
            "username": request.username,
            "email": request.email,
            "password": hashed_password.decode('utf-8'),
            "role": request.role,
            "department": request.department,
            "is_approved": True,  # Admin-created users are auto-approved
            "created_at": datetime.now()
        })
        
        return {
            "success": True,
            "message": "User created successfully",
            "username": request.username
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

@router.put("/{user_id}")
async def update_user(
    user_id: int,
    request: UserUpdateRequest,
    current_user: dict = Depends(verify_token)
):
    """
    Update user information (Admin only)
    """
    try:
        # Check if current user is admin
        admin_query = "SELECT role FROM users WHERE username = ?"
        admin = await database_service.fetch_one(admin_query, {"username": current_user["sub"]})
        
        if not admin or admin["role"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        
        # Check if user exists
        user_query = "SELECT id FROM users WHERE id = ?"
        user = await database_service.fetch_one(user_query, {"id": user_id})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Build update query
        update_fields = []
        params = {"updated_at": datetime.now(), "user_id": user_id}
        
        if request.email is not None:
            update_fields.append("email = ?")
            params["email"] = request.email
            
        if request.role is not None:
            update_fields.append("role = ?")
            params["role"] = request.role
            
        if request.department is not None:
            update_fields.append("department = ?")
            params["department"] = request.department
            
        if request.is_approved is not None:
            update_fields.append("is_approved = ?")
            params["is_approved"] = request.is_approved
        
        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        update_fields.append("updated_at = ?")
        update_query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        
        await database_service.execute_query(update_query, params)
        
        return {
            "success": True,
            "message": "User updated successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user: {str(e)}"
        )

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: dict = Depends(verify_token)
):
    """
    Delete user (Admin only)
    """
    try:
        # Check if current user is admin
        admin_query = "SELECT role FROM users WHERE username = ?"
        admin = await database_service.fetch_one(admin_query, {"username": current_user["sub"]})
        
        if not admin or admin["role"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        
        # Check if user exists
        user_query = "SELECT id FROM users WHERE id = ?"
        user = await database_service.fetch_one(user_query, {"id": user_id})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Delete user
        delete_query = "DELETE FROM users WHERE id = ?"
        await database_service.execute_query(delete_query, {"id": user_id})
        
        return {
            "success": True,
            "message": "User deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete user: {str(e)}"
        )

@router.patch("/{user_id}/approve")
async def approve_user(
    user_id: int,
    current_user: dict = Depends(verify_token)
):
    """
    Approve user registration (Admin only)
    """
    try:
        # Check if current user is admin
        admin_query = "SELECT role FROM users WHERE username = ?"
        admin = await database_service.fetch_one(admin_query, {"username": current_user["sub"]})
        
        if not admin or admin["role"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        
        # Update user approval status
        update_query = "UPDATE users SET is_approved = ?, updated_at = ? WHERE id = ?"
        result = await database_service.execute_query(update_query, {
            "is_approved": True,
            "updated_at": datetime.now(),
            "id": user_id
        })
        
        return {
            "success": True,
            "message": "User approved successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to approve user: {str(e)}"
        )

@router.patch("/{user_id}/reject")
async def reject_user(
    user_id: int,
    current_user: dict = Depends(verify_token)
):
    """
    Reject user registration (Admin only)
    This will delete the user
    """
    try:
        # Check if current user is admin
        admin_query = "SELECT role FROM users WHERE username = ?"
        admin = await database_service.fetch_one(admin_query, {"username": current_user["sub"]})
        
        if not admin or admin["role"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        
        # Delete rejected user
        delete_query = "DELETE FROM users WHERE id = ?"
        await database_service.execute_query(delete_query, {"id": user_id})
        
        return {
            "success": True,
            "message": "User rejected and removed successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reject user: {str(e)}"
        )

@router.get("/attendance-report", response_model=List[AttendanceReport])
async def get_attendance_report(
    location_filter: Optional[str] = Query(None),
    date_range_filter: Optional[str] = Query(None),
    current_user: dict = Depends(verify_token)
):
    """
    Get attendance report with optional filters
    """
    try:
        conditions = []
        params = {}
        
        base_query = """
            SELECT u.id as user_id, u.username, a.date, a.check_in, 
                   a.check_out, a.location
            FROM users u
            LEFT JOIN attendance a ON u.id = a.user_id
        """
        
        if location_filter:
            conditions.append("a.location = ?")
            params["location"] = location_filter
            
        if date_range_filter:
            # Parse date range (implement date range logic)
            conditions.append("a.date >= ?")  # Simplified
            params["date"] = date_range_filter
        
        if conditions:
            base_query += " WHERE " + " AND ".join(conditions)
            
        base_query += " ORDER BY a.date DESC, u.username"
        
        attendance_data = await database_service.fetch_all(base_query, params)
        
        return [
            AttendanceReport(
                user_id=record["user_id"],
                username=record["username"],
                date=record["date"] or "",
                check_in=record.get("check_in"),
                check_out=record.get("check_out"),
                location=record.get("location")
            )
            for record in attendance_data
        ]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get attendance report: {str(e)}"
        )

@router.post("/{user_id}/reset-password")
async def reset_user_password(
    user_id: int,
    new_password: str = Form(...),
    current_user: dict = Depends(verify_token)
):
    """
    Reset user password (Admin only)
    """
    try:
        # Check if current user is admin
        admin_query = "SELECT role FROM users WHERE username = ?"
        admin = await database_service.fetch_one(admin_query, {"username": current_user["sub"]})
        
        if not admin or admin["role"] != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        
        # Hash new password
        import bcrypt
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        # Update password
        update_query = "UPDATE users SET password = ?, updated_at = ? WHERE id = ?"
        await database_service.execute_query(update_query, {
            "password": hashed_password.decode('utf-8'),
            "updated_at": datetime.now(),
            "id": user_id
        })
        
        return {
            "success": True,
            "message": "Password reset successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reset password: {str(e)}"
        )
