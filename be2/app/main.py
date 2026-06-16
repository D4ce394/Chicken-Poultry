"""
AI-FRSS Modular WebSocket Surveillance API v2.0
Simple and clean main entry point following be2v2.0 pattern
"""
import os
import sys
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

# Setup paths
current_dir = os.path.dirname(os.path.abspath(__file__))
be2_dir = os.path.dirname(current_dir)

if be2_dir not in sys.path:
    sys.path.insert(0, be2_dir)

# Import core components
from app.core.config import settings
from app.core.websocket_handler import handle_websocket_connection

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME, 
    version=settings.VERSION
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.ALLOWED_METHODS,
    allow_headers=settings.ALLOWED_HEADERS,
)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "message": f"{settings.PROJECT_NAME} is running",
        "version": settings.VERSION,
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "detail": "Not Found",  # Matching the expected response in HTML
        "version": settings.VERSION,
        "project": settings.PROJECT_NAME
    }

# WebSocket endpoints
@app.websocket("/ws")
async def websocket_simple_endpoint(websocket: WebSocket):
    await handle_websocket_connection(websocket, "test_client", "general")

@app.websocket("/ws/yolo/all")
async def websocket_yolo_all_simple_endpoint(websocket: WebSocket):
    await handle_websocket_connection(websocket, "yolo_client", "yolo_all_parallel")

@app.websocket("/ws/yolo/all/{client_id}")
async def websocket_yolo_all_endpoint(websocket: WebSocket, client_id: str):
    await handle_websocket_connection(websocket, client_id, "yolo_all_parallel")

@app.websocket("/ws/{client_id}")
async def websocket_main_endpoint(websocket: WebSocket, client_id: str):
    await handle_websocket_connection(websocket, client_id, "general")

@app.websocket("/ws/surveillance/{client_id}")
async def websocket_surveillance_endpoint(websocket: WebSocket, client_id: str):
    await handle_websocket_connection(websocket, client_id, "surveillance")

@app.websocket("/ws/admin/{client_id}")
async def websocket_admin_endpoint(websocket: WebSocket, client_id: str):
    await handle_websocket_connection(websocket, client_id, "admin")

# Import and register routers
from app.api.v1 import auth_ws, users_ws, monitoring_ws, alerts_ws
from app.api.v1 import auth_api, users_api, files_api, mobile_api
from app.api.system import router as system_router

# Import mobile_v1 routers for dedicated mobile API
from app.api.mobile_v1.auth import auth_api as mobile_auth_api
from app.api.mobile_v1 import realtime_api as mobile_realtime_api
from app.api.mobile_v1.features import video_upload_api, cctv_api
from app.api.mobile_v1.models import intrusion_api, people_api, security_api, vehicle_api, chicken_api, chicken_stream_api

# WebSocket routers
app.include_router(auth_ws.router, prefix="/ws/auth", tags=["Auth WS"])
app.include_router(users_ws.router, prefix="/ws/users", tags=["Users WS"]) 
app.include_router(monitoring_ws.router, prefix="/ws/monitoring", tags=["Monitoring WS"])
app.include_router(alerts_ws.router, prefix="/ws/alerts", tags=["Alerts WS"])

# REST API routers (v1 - general purpose)
app.include_router(auth_api.router, tags=["Authentication REST"])
app.include_router(users_api.router, tags=["Users REST"])
app.include_router(files_api.router, tags=["Files REST"])
app.include_router(mobile_api.router, tags=["Mobile REST"])
app.include_router(system_router)

# Mobile API routers (mobile_v1 - mobile-specific)
app.include_router(mobile_auth_api.router, prefix="/api/mobile/v1/auth", tags=["Mobile Auth"])
app.include_router(mobile_realtime_api.router, prefix="/api/mobile/v1/realtime", tags=["Mobile Realtime"])
app.include_router(video_upload_api.router, prefix="/api/mobile/v1/video", tags=["Mobile Video"])
app.include_router(cctv_api.router, prefix="/api/mobile/v1/cctv", tags=["Mobile CCTV"])

# Mobile model detection APIs (modular template pattern)
app.include_router(intrusion_api.router, prefix="/api/mobile/v1/intrusion", tags=["Mobile Intrusion"])
app.include_router(people_api.router, prefix="/api/mobile/v1/people", tags=["Mobile People"])
app.include_router(security_api.router, prefix="/api/mobile/v1/security", tags=["Mobile Security"])
app.include_router(vehicle_api.router, prefix="/api/mobile/v1/vehicle", tags=["Mobile Vehicle"])
app.include_router(chicken_api.router, prefix="/api/mobile/v1/chicken", tags=["Chicken Counting"])
app.include_router(chicken_stream_api.router, prefix="/api/mobile/v1/chicken", tags=["Chicken Stream"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.RELOAD
    )
