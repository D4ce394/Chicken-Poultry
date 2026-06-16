from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.auth_service import handle_auth_ws_event

router = APIRouter()
active_connections = []

@router.websocket("/")
async def auth_ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            response = await handle_auth_ws_event(data)
            await websocket.send_text(response)
    except WebSocketDisconnect:
        active_connections.remove(websocket)
