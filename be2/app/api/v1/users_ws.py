from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.user_service import handle_user_ws_event

router = APIRouter()
active_connections = []

@router.websocket("/")
async def user_ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            response = await handle_user_ws_event(data)
            await websocket.send_text(response)
    except WebSocketDisconnect:
        active_connections.remove(websocket)
