"""
System API endpoints for monitoring and management
Separated from main.py to keep it clean (be2v2.0 pattern)
"""

from fastapi import APIRouter, HTTPException
from app.services.websocket_service import websocket_service
from app.services.models_service import yolo_service
from app.services.database_service import database_service
from app.core.config import settings

router = APIRouter(prefix="/api", tags=["System"])

@router.get("/health")
async def get_system_health():
    """Comprehensive system health check"""
    try:
        websocket_stats = websocket_service.manager.get_stats()
        yolo_health = await yolo_service.health_check()
        yolo_stats = await yolo_service.get_service_stats()
        
        return {
            "status": "healthy",
            "version": settings.VERSION,
            "timestamp": websocket_stats.get("timestamp", "unknown"),
            "services": {
                "websocket": {
                    "status": "healthy",
                    "active_connections": websocket_stats.get("active_connections", 0),
                    "peak_connections": websocket_stats.get("peak_connections", 0)
                },
                "yolo": yolo_health,
                "database": {
                    "status": "optional",
                    "available": database_service is not None
                }
            },
            "performance": yolo_stats.get("performance", {}),
            "uptime": websocket_stats.get("uptime_seconds", 0)
        }
    except Exception as e:
        return {
            "status": "error",
            "version": settings.VERSION,
            "error": str(e),
            "timestamp": "unknown"
        }

@router.get("/yolo/stats")
async def get_yolo_statistics():
    """Get detailed YOLO service statistics"""
    try:
        return await yolo_service.get_service_stats()
    except Exception as e:
        return {"error": str(e)}

@router.get("/connections")
async def get_active_connections():
    """Get active WebSocket connections"""
    try:
        stats = websocket_service.manager.get_stats()
        return {
            "total_connections": stats["active_connections"],
            "peak_connections": stats["peak_connections"],
            "connection_details": stats.get("connections", []),
            "groups": stats.get("groups", {}),
            "message_stats": stats.get("messages", {})
        }
    except Exception as e:
        return {"error": str(e)}

@router.delete("/connections/{client_id}")
async def disconnect_client(client_id: str):
    """Manually disconnect a specific client"""
    if client_id in websocket_service.manager.active_connections:
        await websocket_service.manager.disconnect(client_id)
        return {"message": f"Client {client_id} disconnected successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"Client {client_id} not found")
