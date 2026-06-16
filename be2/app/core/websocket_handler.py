"""
WebSocket handlers following be2v2.0 pattern
Centralized WebSocket connection handling - With Parallel YOLO Processing
"""

from fastapi import WebSocket, WebSocketDisconnect
import logging
import json
import asyncio
import base64
from PIL import Image
from io import BytesIO
import time

logger = logging.getLogger(__name__)

# Simple connection manager for testing
class SimpleWebSocketManager:
    def __init__(self):
        self.active_connections = {}
    
    async def connect(self, websocket: WebSocket, client_id: str, connection_type: str = "general"):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client {client_id} connected with type {connection_type}")
    
    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client {client_id} disconnected")

# Global manager instance
simple_manager = SimpleWebSocketManager()

# Mock YOLO detection functions (replace with actual YOLO service calls)
async def detect_intrusion(image_data):
    """Mock intrusion detection"""
    await asyncio.sleep(0.1)
    return {
        "model": "intrusion",
        "classes": ["person", "suspicious_activity"],
        "boxes": [
            {"class": "person", "confidence": 0.85, "x": 100, "y": 100, "w": 100, "h": 100},
            {"class": "suspicious_activity", "confidence": 0.72, "x": 300, "y": 150, "w": 100, "h": 100}
        ],
        "time": 0.1
    }

async def detect_people(image_data):
    """Mock people detection"""
    await asyncio.sleep(0.12)
    return {
        "model": "people",
        "classes": ["person"],
        "boxes": [
            {"class": "person", "confidence": 0.92, "x": 120, "y": 80, "w": 100, "h": 200},
            {"class": "person", "confidence": 0.87, "x": 350, "y": 90, "w": 100, "h": 200}
        ],
        "time": 0.12
    }

async def detect_security_threats(image_data):
    """Mock security threats detection"""
    await asyncio.sleep(0.08)
    return {
        "model": "security_threats",
        "classes": ["weapon"],
        "boxes": [
            {"class": "weapon", "confidence": 0.68, "x": 200, "y": 200, "w": 50, "h": 100}
        ],
        "time": 0.08
    }

async def detect_vehicle(image_data):
    """Mock vehicle detection"""
    await asyncio.sleep(0.11)
    return {
        "model": "vehicle",
        "classes": ["car", "motorcycle"],
        "boxes": [
            {"class": "car", "confidence": 0.94, "x": 50, "y": 300, "w": 250, "h": 200},
            {"class": "motorcycle", "confidence": 0.81, "x": 400, "y": 350, "w": 100, "h": 100}
        ],
        "time": 0.11
    }

async def process_all_yolo_models_parallel(image_data):
    """Process image with all YOLO models in parallel"""
    start_time = time.time()
    
    # Run all detections in parallel
    results = await asyncio.gather(
        detect_intrusion(image_data),
        detect_people(image_data),
        detect_security_threats(image_data),
        detect_vehicle(image_data),
        return_exceptions=True
    )
    
    total_time = time.time() - start_time
    
    # Combine all boxes from all models
    all_boxes = []
    for result in results:
        if not isinstance(result, Exception) and "boxes" in result:
            for box in result["boxes"]:
                all_boxes.append({
                    "model": result["model"],
                    **box
                })
    
    # Simple, clean response
    return {
        "type": "yolo_all_result",
        "time": round(total_time, 3),
        "models": len([r for r in results if not isinstance(r, Exception)]),
        "total_detections": len(all_boxes),
        "boxes": all_boxes,
        "results": {result["model"]: result for result in results if not isinstance(result, Exception)}
    }

async def handle_websocket_connection(websocket: WebSocket, client_id: str, connection_type: str = "general"):
    """Enhanced WebSocket connection handler with parallel YOLO processing"""
    try:
        await simple_manager.connect(websocket, client_id, connection_type)
        
        # Send welcome message
        await websocket.send_text(json.dumps({
            "type": "connection",
            "status": "connected",
            "client_id": client_id,
            "connection_type": connection_type,
            "message": "WebSocket connection established successfully",
            "features": ["parallel_yolo"] if connection_type == "yolo_all_parallel" else ["basic"]
        }))
        
        while True:
            try:
                message_text = await websocket.receive_text()
                logger.info(f"Received message from {client_id}: {message_text[:100]}...")
                
                try:
                    message = json.loads(message_text)
                except json.JSONDecodeError:
                    message = {"type": "raw", "data": message_text}
                
                # Handle different message types
                if connection_type == "yolo_all_parallel" and message.get("type") == "detect_all":
                    # Parallel YOLO detection
                    image_data = message.get("image_data", "")
                    
                    await websocket.send_text(json.dumps({
                        "type": "processing_started",
                        "message": "Processing with all YOLO models in parallel...",
                        "models": ["intrusion", "people", "security_threats", "vehicle"]
                    }))
                    
                    # Process with all models
                    result = await process_all_yolo_models_parallel(image_data)
                    await websocket.send_text(json.dumps(result))
                    
                elif message.get("type") == "ping":
                    # Ping-pong for connection testing
                    await websocket.send_text(json.dumps({
                        "type": "pong",
                        "timestamp": time.time(),
                        "client_id": client_id
                    }))
                    
                else:
                    # Echo message back with timestamp
                    response = {
                        "type": "echo",
                        "original_message": message,
                        "client_id": client_id,
                        "timestamp": time.time(),
                        "connection_type": connection_type,
                        "status": "received"
                    }
                    
                    await websocket.send_text(json.dumps(response))
                
            except WebSocketDisconnect:
                logger.info(f"Client {client_id} disconnected normally")
                break
            except Exception as e:
                logger.error(f"Error handling message from {client_id}: {str(e)}")
                await websocket.send_text(json.dumps({
                    "type": "error",
                    "message": f"Error processing message: {str(e)}",
                    "client_id": client_id
                }))
                break
                
    except Exception as e:
        logger.error(f"WebSocket connection error for {client_id}: {str(e)}")
    finally:
        simple_manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")
