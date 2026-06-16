import json
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Set, Optional
from fastapi import WebSocket
from collections import defaultdict
import time

# Import YOLO service for real detection
from app.services.models_service import yolo_service

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Optimized WebSocket connection manager for multiple clients and streaming"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.connection_types: Dict[str, str] = {}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        self.message_queue: Dict[str, asyncio.Queue] = {}
        self.processing_tasks: Dict[str, asyncio.Task] = {}
        
        # Performance monitoring
        self.stats = {
            "total_connections": 0,
            "total_messages": 0,
            "total_detections": 0,
            "active_since": datetime.now(),
            "peak_connections": 0
        }
        
        # Connection groups for broadcasting
        self.connection_groups: Dict[str, Set[str]] = defaultdict(set)
    
    async def connect(self, websocket: WebSocket, client_id: str, connection_type: str = "general"):
        """Connect WebSocket client with optimized handling"""
        try:
            await websocket.accept()
            
            # Store connection info
            self.active_connections[client_id] = websocket
            self.connection_types[client_id] = connection_type
            self.connection_metadata[client_id] = {
                "connected_at": datetime.now(),
                "last_activity": datetime.now(),
                "message_count": 0,
                "detection_count": 0,
                "connection_type": connection_type
            }
            
            # Add to connection group
            self.connection_groups[connection_type].add(client_id)
            
            # Create message queue for this client
            self.message_queue[client_id] = asyncio.Queue(maxsize=100)
            
            # Start message processing task
            self.processing_tasks[client_id] = asyncio.create_task(
                self._process_client_messages(client_id)
            )
            
            # Update stats
            self.stats["total_connections"] += 1
            current_active = len(self.active_connections)
            if current_active > self.stats["peak_connections"]:
                self.stats["peak_connections"] = current_active
            
            logger.info(f"Client {client_id} connected (type: {connection_type}, total: {current_active})")
            
            # Send optimized welcome message
            await self._queue_message(client_id, {
                "type": "connection_established",
                "client_id": client_id,
                "connection_type": connection_type,
                "server_info": {
                    "version": "2.0.0",
                    "capabilities": ["yolo_detection", "multi_model", "real_time_alerts"],
                    "supported_models": ["intrusion", "people", "security_threats", "vehicle"]
                },
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error connecting client {client_id}: {e}")
            raise
    
    def disconnect(self, client_id: str):
        """Optimized disconnect with cleanup"""
        if client_id in self.active_connections:
            # Cancel processing task
            if client_id in self.processing_tasks:
                self.processing_tasks[client_id].cancel()
                del self.processing_tasks[client_id]
            
            # Remove from groups
            connection_type = self.connection_types.get(client_id, "general")
            self.connection_groups[connection_type].discard(client_id)
            
            # Cleanup all data
            del self.active_connections[client_id]
            del self.connection_types[client_id]
            del self.connection_metadata[client_id]
            
            if client_id in self.message_queue:
                del self.message_queue[client_id]
            
            logger.info(f"Client {client_id} disconnected (remaining: {len(self.active_connections)})")
    
    async def _queue_message(self, client_id: str, message: Dict[str, Any]):
        """Queue message for client with overflow protection"""
        if client_id in self.message_queue:
            try:
                await self.message_queue[client_id].put(message)
            except asyncio.QueueFull:
                logger.warning(f"Message queue full for client {client_id}, dropping oldest message")
                try:
                    self.message_queue[client_id].get_nowait()  # Remove oldest
                    await self.message_queue[client_id].put(message)
                except asyncio.QueueEmpty:
                    pass
    
    async def _process_client_messages(self, client_id: str):
        """Process queued messages for a client"""
        websocket = self.active_connections[client_id]
        
        try:
            while client_id in self.active_connections:
                try:
                    # Get message from queue with timeout
                    message = await asyncio.wait_for(
                        self.message_queue[client_id].get(), 
                        timeout=1.0
                    )
                    
                    # Send message
                    await websocket.send_text(json.dumps(message))
                    
                    # Update metadata
                    if client_id in self.connection_metadata:
                        self.connection_metadata[client_id]["last_activity"] = datetime.now()
                        self.connection_metadata[client_id]["message_count"] += 1
                    
                except asyncio.TimeoutError:
                    # Send heartbeat if no messages
                    await websocket.send_text(json.dumps({
                        "type": "heartbeat",
                        "timestamp": datetime.now().isoformat()
                    }))
                except Exception as e:
                    logger.error(f"Error sending message to {client_id}: {e}")
                    break
        except Exception as e:
            logger.error(f"Message processing error for {client_id}: {e}")
        finally:
            # Cleanup on exit
            if client_id in self.active_connections:
                self.disconnect(client_id)
    
    async def send_message(self, client_id: str, message: Dict[str, Any]):
        """Send message to specific client via queue"""
        await self._queue_message(client_id, message)
    
    async def broadcast_to_group(self, connection_type: str, message: Dict[str, Any]):
        """Broadcast message to all clients of a specific type"""
        clients = self.connection_groups.get(connection_type, set())
        if clients:
            logger.info(f"Broadcasting to {len(clients)} clients of type {connection_type}")
            
            # Send to all clients in parallel
            tasks = []
            for client_id in clients.copy():  # Copy to avoid modification during iteration
                tasks.append(self._queue_message(client_id, message))
            
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
    
    async def broadcast_alert(self, alert_data: Dict[str, Any]):
        """Broadcast security alert to all relevant clients"""
        alert_message = {
            "type": "security_alert",
            "alert": alert_data,
            "timestamp": datetime.now().isoformat(),
            "priority": alert_data.get("priority", "medium")
        }
        
        # Send to surveillance and admin clients
        await asyncio.gather(
            self.broadcast_to_group("surveillance", alert_message),
            self.broadcast_to_group("admin", alert_message),
            return_exceptions=True
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive connection statistics"""
        current_time = datetime.now()
        uptime = (current_time - self.stats["active_since"]).total_seconds()
        
        # Calculate group stats
        group_stats = {}
        for group_type, clients in self.connection_groups.items():
            group_stats[group_type] = len(clients)
        
        return {
            "active_connections": len(self.active_connections),
            "peak_connections": self.stats["peak_connections"],
            "total_connections_ever": self.stats["total_connections"],
            "total_messages": self.stats["total_messages"],
            "total_detections": self.stats["total_detections"],
            "uptime_seconds": uptime,
            "connection_groups": group_stats,
            "clients": list(self.active_connections.keys()),
            "message_queue_sizes": {
                client_id: queue.qsize() 
                for client_id, queue in self.message_queue.items()
            }
        }

class WebSocketService:
    """WebSocket message handler service - Based on be3 pattern"""
    
    def __init__(self):
        self.manager = WebSocketManager()
    
    async def handle_message(self, client_id: str, message_text: str):
        """Optimized message handling with rate limiting and validation"""
        try:
            # Update stats
            self.manager.stats["total_messages"] += 1
            if client_id in self.manager.connection_metadata:
                self.manager.connection_metadata[client_id]["last_activity"] = datetime.now()
            
            # Parse message
            message = json.loads(message_text)
            message_type = message.get("type")
            
            # Add processing start time for performance monitoring
            message["_processing_start"] = time.time()
            
            # Rate limiting check (optional)
            if await self._check_rate_limit(client_id):
                await self.manager.send_message(client_id, {
                    "type": "error",
                    "error": "Rate limit exceeded",
                    "timestamp": datetime.now().isoformat()
                })
                return
            
            # Route messages based on type (optimized routing)
            handler_map = {
                "ping": self._handle_ping,
                "check_image": self._handle_check_image,
                "multi_model_detection": self._handle_multi_model_detection,
                "get_available_models": self._handle_get_available_models,
                "get_system_stats": self._handle_get_system_stats,
                "rtsp_stream_start": self._handle_rtsp_stream_start,
                "rtsp_stream_stop": self._handle_rtsp_stream_stop,
                # Legacy handlers for backward compatibility
                "recognize_face": self._handle_recognize_face,
                "insert_face": self._handle_insert_face,
                "insert_admin": self._handle_insert_admin,
                "LOGIN_REQUEST": self._handle_login,
                "GET_PROFILE_REQUEST": self._handle_get_profile,
                "UPDATE_PROFILE_REQUEST": self._handle_update_profile,
                "INSERT_ATTENDANCE": self._handle_insert_attendance,
            }
            
            handler = handler_map.get(message_type)
            if handler:
                # Execute handler asynchronously
                await handler(client_id, message)
            else:
                await self.manager.send_message(client_id, {
                    "type": "error",
                    "error": f"Unknown message type: {message_type}",
                    "supported_types": list(handler_map.keys()),
                    "timestamp": datetime.now().isoformat()
                })
                
        except json.JSONDecodeError as e:
            await self.manager.send_message(client_id, {
                "type": "error",
                "error": "Invalid JSON format",
                "details": str(e),
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            logger.error(f"Error handling message from {client_id}: {str(e)}")
            await self.manager.send_message(client_id, {
                "type": "error",
                "error": f"Internal server error: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })
    
    async def _check_rate_limit(self, client_id: str) -> bool:
        """Simple rate limiting (can be enhanced)"""
        # For now, just return False (no limit)
        # TODO: Implement proper rate limiting with Redis or in-memory store
        return False
    
    # Optimized message handlers
    async def _handle_ping(self, client_id: str, message: dict):
        """Handle ping with enhanced info"""
        await self.manager.send_message(client_id, {
            "type": "pong",
            "server_time": datetime.now().isoformat(),
            "client_id": client_id,
            "connection_uptime": self._get_connection_uptime(client_id),
            "processing_time": time.time() - message.get("_processing_start", time.time())
        })
    
    async def _handle_get_system_stats(self, client_id: str, message: dict):
        """Handle system statistics request"""
        stats = self.manager.get_stats()
        stats["yolo_stats"] = await yolo_service.get_service_stats()
        
        await self.manager.send_message(client_id, {
            "type": "system_stats",
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        })
    
    async def _handle_rtsp_stream_start(self, client_id: str, message: dict):
        """Handle RTSP stream start (future implementation)"""
        await self.manager.send_message(client_id, {
            "type": "rtsp_stream_response",
            "status": "not_implemented",
            "message": "RTSP streaming will be implemented in Phase 2",
            "timestamp": datetime.now().isoformat()
        })
    
    async def _handle_rtsp_stream_stop(self, client_id: str, message: dict):
        """Handle RTSP stream stop (future implementation)"""
        await self.manager.send_message(client_id, {
            "type": "rtsp_stream_response",
            "status": "not_implemented",
            "message": "RTSP streaming will be implemented in Phase 2",
            "timestamp": datetime.now().isoformat()
        })
    
    def _get_connection_uptime(self, client_id: str) -> float:
        """Get connection uptime in seconds"""
        if client_id in self.manager.connection_metadata:
            connected_at = self.manager.connection_metadata[client_id]["connected_at"]
            return (datetime.now() - connected_at).total_seconds()
        return 0.0
    
    async def _handle_recognize_face(self, client_id: str, message: dict):
        await self.manager.send_message(client_id, {
            "type": "face_recognition_result",
            "status": "not_implemented",
            "message": "Face recognition coming soon",
            "timestamp": datetime.now().isoformat()
        })
    
    async def _handle_insert_face(self, client_id: str, message: dict):
        await self.manager.send_message(client_id, {
            "type": "face_insert_result",
            "status": "not_implemented",
            "message": "Face insertion coming soon",
            "timestamp": datetime.now().isoformat()
        })
    
    async def _handle_insert_admin(self, client_id: str, message: dict):
        await self.manager.send_message(client_id, {
            "type": "admin_insert_result",
            "status": "not_implemented",
            "message": "Admin management coming soon",
            "timestamp": datetime.now().isoformat()
        })
    
    async def _handle_login(self, client_id: str, message: dict):
        await self.manager.send_message(client_id, {
            "type": "login_response",
            "status": "not_implemented",
            "message": "Authentication coming soon",
            "timestamp": datetime.now().isoformat()
        })
    
    async def _handle_get_profile(self, client_id: str, message: dict):
        await self.manager.send_message(client_id, {
            "type": "profile_response",
            "status": "not_implemented",
            "message": "Profile system coming soon",
            "timestamp": datetime.now().isoformat()
        })
    
    async def _handle_update_profile(self, client_id: str, message: dict):
        await self.manager.send_message(client_id, {
            "type": "profile_update_result",
            "status": "not_implemented",
            "message": "Profile update coming soon",
            "timestamp": datetime.now().isoformat()
        })
    
    async def _handle_insert_attendance(self, client_id: str, message: dict):
        await self.manager.send_message(client_id, {
            "type": "attendance_result",
            "status": "not_implemented",
            "message": "Attendance system coming soon",
            "timestamp": datetime.now().isoformat()
        })
    
    async def _handle_check_image(self, client_id: str, message: dict):
        """Optimized single model detection with performance monitoring"""
        message_id = message.get("message_id", f"detection_{int(datetime.now().timestamp())}")
        start_time = time.time()
        
        try:
            # Extract and validate parameters
            image_data = message.get("image_data")
            model_type = message.get("model_name", message.get("model", "intrusion"))
            confidence = float(message.get("confidence", 0.5))
            iou_threshold = float(message.get("iou_threshold", 0.45))
            
            # Validation
            if not image_data:
                await self.manager.send_message(client_id, {
                    "type": "error",
                    "message_id": message_id,
                    "error": "No image data provided",
                    "timestamp": datetime.now().isoformat()
                })
                return
            
            if confidence < 0.0 or confidence > 1.0:
                confidence = 0.5
                
            if iou_threshold < 0.0 or iou_threshold > 1.0:
                iou_threshold = 0.45
            
            # Perform detection with performance monitoring
            detection_start = time.time()
            result = await yolo_service.detect_objects(
                model_type=model_type,
                image_data=image_data,
                confidence=confidence,
                iou_threshold=iou_threshold
            )
            detection_time = time.time() - detection_start
            
            # Update stats
            self.manager.stats["total_detections"] += 1
            if client_id in self.manager.connection_metadata:
                self.manager.connection_metadata[client_id]["detection_count"] += 1
            
            # Send comprehensive result
            response = {
                "type": "detection_result",
                "message_id": message_id,
                "model_type": model_type,
                "success": result.get("success", True),
                "detections": result.get("detections", []),
                "total_detections": result.get("total_detections", 0),
                "processing_time": result.get("processing_time", detection_time),
                "image_size": result.get("image_size", []),
                "parameters": {
                    "confidence": confidence,
                    "iou_threshold": iou_threshold
                },
                "performance": {
                    "total_time": time.time() - start_time,
                    "detection_time": detection_time,
                    "queue_time": detection_start - start_time
                },
                "timestamp": datetime.now().isoformat()
            }
            
            await self.manager.send_message(client_id, response)
            
            # Broadcast alert if detections found
            if result.get("detections") and len(result["detections"]) > 0:
                await self._broadcast_detection_alert(client_id, model_type, result)
            
        except Exception as e:
            await self.manager.send_message(client_id, {
                "type": "error",
                "message_id": message_id,
                "error": f"Detection failed: {str(e)}",
                "processing_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            })
    
    async def _handle_multi_model_detection(self, client_id: str, message: dict):
        """Optimized multi-model detection with parallel processing"""
        message_id = message.get("message_id", f"multi_detection_{int(datetime.now().timestamp())}")
        start_time = time.time()
        
        try:
            # Extract parameters
            image_data = message.get("image_data")
            models_to_use = message.get("models", ["intrusion", "people", "security_threats", "vehicle"])
            confidence = float(message.get("confidence", 0.5))
            iou_threshold = float(message.get("iou_threshold", 0.45))
            
            if not image_data:
                await self.manager.send_message(client_id, {
                    "type": "error",
                    "message_id": message_id,
                    "error": "No image data provided",
                    "timestamp": datetime.now().isoformat()
                })
                return
            
            # Parallel processing of multiple models
            detection_start = time.time()
            tasks = []
            for model in models_to_use:
                task = yolo_service.detect_objects(
                    model_type=model,
                    image_data=image_data,
                    confidence=confidence,
                    iou_threshold=iou_threshold
                )
                tasks.append((model, task))
            
            # Execute all detections in parallel
            results = {}
            total_detections = 0
            successful_models = []
            failed_models = []
            
            for model, task in tasks:
                try:
                    result = await task
                    results[model] = result
                    if result.get("detections"):
                        total_detections += len(result["detections"])
                        successful_models.append(model)
                except Exception as e:
                    results[model] = {
                        "success": False,
                        "error": str(e),
                        "detections": [],
                        "processing_time": 0
                    }
                    failed_models.append(model)
            
            detection_time = time.time() - detection_start
            
            # Update stats
            self.manager.stats["total_detections"] += total_detections
            if client_id in self.manager.connection_metadata:
                self.manager.connection_metadata[client_id]["detection_count"] += len(models_to_use)
            
            # Send comprehensive results
            response = {
                "type": "multi_detection_result",
                "message_id": message_id,
                "results": results,
                "summary": {
                    "total_detections": total_detections,
                    "models_successful": successful_models,
                    "models_failed": failed_models,
                    "models_requested": models_to_use,
                    "success_rate": f"{len(successful_models)}/{len(models_to_use)}"
                },
                "performance": {
                    "total_time": time.time() - start_time,
                    "detection_time": detection_time,
                    "parallel_efficiency": detection_time / (len(models_to_use) * 0.1)  # Rough estimate
                },
                "timestamp": datetime.now().isoformat()
            }
            
            await self.manager.send_message(client_id, response)
            
            # Broadcast alert if any detections found
            if total_detections > 0:
                await self._broadcast_multi_detection_alert(client_id, successful_models, results)
            
        except Exception as e:
            await self.manager.send_message(client_id, {
                "type": "error",
                "message_id": message_id,
                "error": f"Multi-model detection failed: {str(e)}",
                "processing_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            })
    
    async def _broadcast_detection_alert(self, client_id: str, model_type: str, result: dict):
        """Broadcast detection alert to relevant clients"""
        alert_data = {
            "source_client": client_id,
            "model_type": model_type,
            "detection_count": len(result.get("detections", [])),
            "confidence_avg": sum(d.get("confidence", 0) for d in result.get("detections", [])) / max(1, len(result.get("detections", []))),
            "timestamp": datetime.now().isoformat()
        }
        
        await self.manager.broadcast_alert(alert_data)
    
    async def _broadcast_multi_detection_alert(self, client_id: str, models: list, results: dict):
        """Broadcast multi-model detection alert"""
        total_objects = sum(len(results[model].get("detections", [])) for model in models)
        
        alert_data = {
            "source_client": client_id,
            "models": models,
            "total_detections": total_objects,
            "results_summary": {
                model: len(results[model].get("detections", []))
                for model in models
            },
            "timestamp": datetime.now().isoformat()
        }
        
        await self.manager.broadcast_alert(alert_data)
    
    async def _handle_get_available_models(self, client_id: str, message: dict):
        """Handle get available models request"""
        message_id = message.get("message_id", f"models_{int(datetime.now().timestamp())}")
        
        try:
            models_info = await yolo_service.list_all_models()
            await self.manager.send_message(client_id, {
                "type": "available_models",
                "message_id": message_id,
                "models": models_info,
                "timestamp": datetime.now().isoformat()
            })
        except Exception as e:
            await self.manager.send_message(client_id, {
                "type": "error",
                "message_id": message_id,
                "error": f"Failed to get models info: {str(e)}",
                "timestamp": datetime.now().isoformat()
            })

# Global instance
websocket_service = WebSocketService()
