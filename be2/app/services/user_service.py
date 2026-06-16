import json
from app.services.database_service import database_service

async def handle_user_ws_event(data: str) -> str:
    payload = json.loads(data)
    action = payload.get("action")
    
    if action == "get_users":
        try:
            query = "SELECT id, name, email, role_id, created_at FROM users"
            results = await database_service.fetch_all(query)
            
            users_data = [
                {
                    "id": user["id"],
                    "name": user.get("name", user.get("fullname")),
                    "email": user["email"],
                    "role_id": user.get("role_id"),
                    "created_at": str(user.get("created_at", ""))
                }
                for user in results
            ]
            
            return json.dumps({"status": "success", "users": users_data})
            
        except Exception as e:
            return json.dumps({"status": "error", "message": f"Failed to fetch users: {str(e)}"})
            
    elif action == "get_user":
        user_id = payload.get("user_id")
        try:
            query = "SELECT * FROM users WHERE id = :user_id"
            result = await database_service.fetch_one(query, {"user_id": user_id})
            
            if result:
                return json.dumps({
                    "status": "success",
                    "user": {
                        "id": result["id"],
                        "name": result.get("name", result.get("fullname")),
                        "email": result["email"],
                        "role_id": result.get("role_id")
                    }
                })
            else:
                return json.dumps({"status": "error", "message": "User not found"})
                
        except Exception as e:
            return json.dumps({"status": "error", "message": f"Failed to fetch user: {str(e)}"})
            
    else:
        return json.dumps({"status": "error", "message": "Unknown action"})
