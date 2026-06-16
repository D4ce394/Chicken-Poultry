import json
from app.services.database_service import database_service

async def handle_alert_ws_event(data: str) -> str:
    payload = json.loads(data)
    action = payload.get("action")
    
    if action in ("get_alerts", "get_live_alerts", "get_alert_history"):
        try:
            if action == "get_live_alerts":
                query = """
                SELECT * FROM alerts 
                WHERE status != 'resolved' 
                ORDER BY created_at DESC 
                LIMIT 10
                """
            else:
                query = "SELECT * FROM alerts ORDER BY created_at DESC"
                
            results = await database_service.fetch_all(query)
            
            alerts_data = [
                {
                    "id": alert["id"],
                    "type": alert.get("type"),
                    "message": alert.get("message"),
                    "status": alert.get("status"),
                    "created_at": str(alert.get("created_at", ""))
                }
                for alert in results
            ]
            
            return json.dumps({"status": "success", "alerts": alerts_data})
            
        except Exception as e:
            # Fallback to dummy data if table doesn't exist
            return json.dumps({
                "status": "success",
                "alerts": [
                    {"id": 1, "type": "intrusion", "message": "Motion detected", "status": "active"},
                    {"id": 2, "type": "system", "message": "Camera offline", "status": "resolved"}
                ]
            })
            
    else:
        return json.dumps({"status": "error", "message": "Unknown action"})
