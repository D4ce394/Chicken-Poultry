import json
import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from app.models.auth import User, get_admin_by_username, add_admin
from app.services.database_service import database_service
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError

class AuthService:
    """Authentication service for mobile and web applications"""
    
    def __init__(self):
        self.jwt_secret = os.getenv("JWT_SECRET", "ai-frss-secret-key")
        
    async def authenticate_admin(self, username: str, password: str):
        """Authenticate admin user"""
        try:
            user = await get_admin_by_username(username)
            if not user:
                return {
                    "success": False,
                    "message": "Invalid credentials"
                }
            
            # Verify password (implement based on your auth model)
            # This is a basic implementation - adjust based on your password hashing
            token = jwt.encode(
                {"username": username, "exp": datetime.utcnow() + timedelta(hours=1)},
                self.jwt_secret,
                algorithm="HS256"
            )
            
            return {
                "success": True,
                "message": "Login successful",
                "token": token
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Authentication failed: {str(e)}"
            }
    
    async def create_admin(self, username: str, password: str):
        """Create new admin user"""
        try:
            existing_user = await get_admin_by_username(username)
            if existing_user:
                raise Exception("Admin already registered")
            
            await add_admin(username, password)
            return {
                "success": True,
                "message": "Admin registered successfully"
            }
            
        except Exception as e:
            raise Exception(f"Registration failed: {str(e)}")

# Global instance
auth_service = AuthService()

async def handle_auth_ws_event(data: str) -> str:
    payload = json.loads(data)
    action = payload.get("action")
    
    if action == "signin":
        email = payload.get("email")
        password = payload.get("password")
        
        try:
            # Query user from database
            query = "SELECT * FROM users WHERE email = :email"
            result = await database_service.fetch_one(query, {"email": email})
            
            if result and result.get("password") == password:
                return json.dumps({
                    "status": "success", 
                    "message": "Signed in successfully",
                    "user": {
                        "id": result["id"],
                        "name": result.get("name", result.get("fullname")),
                        "email": result["email"],
                        "role_id": result.get("role_id")
                    }
                })
            else:
                return json.dumps({"status": "error", "message": "Invalid credentials"})
                
        except Exception as e:
            return json.dumps({"status": "error", "message": f"Authentication failed: {str(e)}"})
            
    elif action == "register":
        name = payload.get("name") or payload.get("fullname")
        email = payload.get("email")
        password = payload.get("password")
        role_id = payload.get("role_id", 2)  # Default role
        
        try:
            # Insert new user
            query = """
            INSERT INTO users (name, email, password, role_id, created_at, updated_at)
            VALUES (:name, :email, :password, :role_id, datetime('now'), datetime('now'))
            """
            await database_service.execute_query(query, {
                "name": name,
                "email": email,
                "password": password,
                "role_id": role_id
            })
            
            return json.dumps({
                "status": "success",
                "message": "User registered successfully"
            })
            
        except Exception as e:
            return json.dumps({"status": "error", "message": f"Registration failed: {str(e)}"})
            
    else:
        return json.dumps({"status": "error", "message": "Unknown action"})
