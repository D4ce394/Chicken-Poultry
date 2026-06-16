"""
Real-time Detection WebSocket API
Handles live video detection via WebSocket
"""
from fastapi import APIRouter, WebSocket, HTTPException, Query
from typing import Optional

from app.services.realtime_service import realtime_service

router = APIRouter()

@router.websocket("/live-detection")
async def websocket_live_detection(
    websocket: WebSocket,
    session_id: Optional[str] = Query(None, description="Optional session ID for reconnection")
):
    """
    WebSocket endpoint for real-time video detection
    
    **Usage:**
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/mobile/v1/realtime/live-detection');
    
    // Send frame for detection
    ws.send(JSON.stringify({
        type: "frame",
        data: "base64_image_data",
        frame_id: "unique_frame_id"
    }));
    
    // Update configuration
    ws.send(JSON.stringify({
        type: "config",
        data: {
            models: ["intrusion", "people"],
            confidence: 0.6,
            max_fps: 10
        }
    }));
    
    // Get statistics
    ws.send(JSON.stringify({
        type: "get_stats"
    }));
    ```
    
    **Response Format:**
    ```json
    {
        "type": "detection_result",
        "frame_id": "frame_123",
        "timestamp": "2025-07-29T10:30:00",
        "results": {
            "intrusion": {
                "detections": [...],
                "total_detections": 2,
                "processing_time": 0.15
            }
        },
        "stats": {
            "frames_processed": 150,
            "total_detections": 45
        }
    }
    ```
    """
    await realtime_service.handle_websocket_connection(websocket, session_id)

@router.get("/sessions")
async def list_active_sessions():
    """
    List active WebSocket sessions
    """
    try:
        sessions = []
        for session_id in realtime_service.connection_manager.active_connections.keys():
            config = realtime_service.connection_manager.get_session_config(session_id)
            stats = realtime_service.connection_manager.get_session_stats(session_id)
            
            sessions.append({
                "session_id": session_id,
                "config": config,
                "stats": stats
            })
        
        return {
            "active_sessions": len(sessions),
            "sessions": sessions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/sessions/{session_id}")
async def disconnect_session(session_id: str):
    """
    Force disconnect a WebSocket session
    
    - **session_id**: Session ID to disconnect
    """
    try:
        if session_id in realtime_service.connection_manager.active_connections:
            realtime_service.connection_manager.disconnect(session_id)
            return {"message": f"Session {session_id} disconnected"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
