"""
Real-time Detection Service
Handles WebSocket connections for live video detection
"""
import asyncio
import json
import uuid
from typing import Dict, Set, Optional, List
from fastapi import WebSocket, WebSocketDisconnect
import logging
from datetime import datetime
import base64

from app.services.models_service import yolo_service

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for real-time detection"""
    
    def __init__(self):
        # Active connections per session
        self.active_connections: Dict[str, WebSocket] = {}
        # Session configurations
        self.session_configs: Dict[str, Dict] = {}
        # Detection statistics
        self.session_stats: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str = None) -> str:
        """Connect new WebSocket session"""
        await websocket.accept()
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        self.active_connections[session_id] = websocket
        self.session_configs[session_id] = {
            "models": ["intrusion"],  # Default model
            "confidence": 0.5,
            "iou_threshold": 0.45,
            "max_fps": 10,  # Limit FPS for performance
            "created_at": datetime.now().isoformat()
        }
        self.session_stats[session_id] = {
            "frames_processed": 0,
            "total_detections": 0,
            "last_detection": None,
            "start_time": datetime.now().isoformat()
        }
        
        logger.info(f"WebSocket connected: {session_id}")
        return session_id
    
    def disconnect(self, session_id: str):
        """Disconnect WebSocket session"""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
            del self.session_configs[session_id]
            del self.session_stats[session_id]
            logger.info(f"WebSocket disconnected: {session_id}")
    
    async def send_personal_message(self, message: dict, session_id: str):
        """Send message to specific session"""
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Failed to send message to {session_id}: {e}")
                self.disconnect(session_id)
    
    def get_session_config(self, session_id: str) -> Dict:
        """Get session configuration"""
        return self.session_configs.get(session_id, {})
    
    def update_session_config(self, session_id: str, config: Dict):
        """Update session configuration"""
        if session_id in self.session_configs:
            self.session_configs[session_id].update(config)
    
    def get_session_stats(self, session_id: str) -> Dict:
        """Get session statistics"""
        return self.session_stats.get(session_id, {})
    
    def update_session_stats(self, session_id: str, stats: Dict):
        """Update session statistics"""
        if session_id in self.session_stats:
            self.session_stats[session_id].update(stats)

class RealTimeDetectionService:
    """Service for real-time video detection via WebSocket"""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.frame_queues: Dict[str, asyncio.Queue] = {}
        self.processing_tasks: Dict[str, asyncio.Task] = {}
    
    async def handle_websocket_connection(self, websocket: WebSocket, session_id: str = None):
        """Handle new WebSocket connection"""
        session_id = await self.connection_manager.connect(websocket, session_id)
        
        # Create frame queue for this session
        self.frame_queues[session_id] = asyncio.Queue(maxsize=10)  # Buffer 10 frames
        
        # Start processing task
        self.processing_tasks[session_id] = asyncio.create_task(
            self._process_frames_for_session(session_id)
        )
        
        try:
            # Send initial configuration
            await self.connection_manager.send_personal_message({
                "type": "connection_established",
                "session_id": session_id,
                "config": self.connection_manager.get_session_config(session_id)
            }, session_id)
            
            # Listen for incoming messages
            while True:
                try:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    await self._handle_message(session_id, message)
                    
                except WebSocketDisconnect:
                    break
                except json.JSONDecodeError:
                    await self.connection_manager.send_personal_message({
                        "type": "error",
                        "message": "Invalid JSON format"
                    }, session_id)
                except Exception as e:
                    logger.error(f"WebSocket error for {session_id}: {e}")
                    await self.connection_manager.send_personal_message({
                        "type": "error",
                        "message": str(e)
                    }, session_id)
        
        except WebSocketDisconnect:
            pass
        finally:
            # Cleanup
            if session_id in self.processing_tasks:
                self.processing_tasks[session_id].cancel()
                del self.processing_tasks[session_id]
            if session_id in self.frame_queues:
                del self.frame_queues[session_id]
            self.connection_manager.disconnect(session_id)
    
    async def _handle_message(self, session_id: str, message: Dict):
        """Handle incoming WebSocket message"""
        message_type = message.get("type")
        
        if message_type == "frame":
            # Add frame to processing queue
            frame_data = message.get("data")
            if frame_data and session_id in self.frame_queues:
                try:
                    # Non-blocking put, drop frame if queue is full
                    self.frame_queues[session_id].put_nowait({
                        "frame_data": frame_data,
                        "timestamp": datetime.now().isoformat(),
                        "frame_id": message.get("frame_id", str(uuid.uuid4()))
                    })
                except asyncio.QueueFull:
                    # Drop frame if queue is full (real-time priority)
                    pass
        
        elif message_type == "config":
            # Update session configuration
            config_updates = message.get("data", {})
            self.connection_manager.update_session_config(session_id, config_updates)
            
            await self.connection_manager.send_personal_message({
                "type": "config_updated",
                "config": self.connection_manager.get_session_config(session_id)
            }, session_id)
        
        elif message_type == "get_stats":
            # Send current statistics
            stats = self.connection_manager.get_session_stats(session_id)
            await self.connection_manager.send_personal_message({
                "type": "stats",
                "data": stats
            }, session_id)
        
        else:
            await self.connection_manager.send_personal_message({
                "type": "error",
                "message": f"Unknown message type: {message_type}"
            }, session_id)
    
    async def _process_frames_for_session(self, session_id: str):
        """Process frames for a specific session"""
        while session_id in self.frame_queues:
            try:
                # Wait for next frame
                frame_info = await asyncio.wait_for(
                    self.frame_queues[session_id].get(), 
                    timeout=1.0
                )
                
                # Get session config
                config = self.connection_manager.get_session_config(session_id)
                
                # Process frame with configured models
                results = {}
                for model_type in config.get("models", ["intrusion"]):
                    try:
                        detection_result = await yolo_service.detect_objects(
                            model_type=model_type,
                            image_data=frame_info["frame_data"],
                            confidence=config.get("confidence", 0.5),
                            iou_threshold=config.get("iou_threshold", 0.45)
                        )
                        results[model_type] = detection_result
                    except Exception as e:
                        logger.error(f"Detection failed for {model_type}: {e}")
                        results[model_type] = {"error": str(e)}
                
                # Update statistics
                stats = self.connection_manager.get_session_stats(session_id)
                total_detections = sum(
                    r.get("total_detections", 0) for r in results.values() 
                    if "error" not in r
                )
                
                stats.update({
                    "frames_processed": stats.get("frames_processed", 0) + 1,
                    "total_detections": stats.get("total_detections", 0) + total_detections,
                    "last_detection": datetime.now().isoformat() if total_detections > 0 else stats.get("last_detection")
                })
                self.connection_manager.update_session_stats(session_id, stats)
                
                # Send results back
                await self.connection_manager.send_personal_message({
                    "type": "detection_result",
                    "frame_id": frame_info["frame_id"],
                    "timestamp": frame_info["timestamp"],
                    "results": results,
                    "stats": stats
                }, session_id)
                
            except asyncio.TimeoutError:
                # No frames to process, continue
                continue
            except asyncio.CancelledError:
                # Task cancelled, exit
                break
            except Exception as e:
                logger.error(f"Frame processing error for {session_id}: {e}")
                await self.connection_manager.send_personal_message({
                    "type": "error",
                    "message": f"Processing error: {str(e)}"
                }, session_id)

# Global service instance
realtime_service = RealTimeDetectionService()
