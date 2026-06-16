"""
CCTV/IP Camera Service
Handles IP camera connections and continuous monitoring
"""
import asyncio
try:
    import cv2
except Exception:
    cv2 = None
import json
import uuid
from typing import Dict, List, Optional, Callable
from datetime import datetime, timedelta
import logging
import base64
from threading import Thread
import time
from urllib.parse import urlparse

from app.services.models_service import yolo_service

logger = logging.getLogger(__name__)

class CCTVCamera:
    """Represents a single CCTV/IP camera"""
    
    def __init__(self, camera_id: str, stream_url: str, name: str = None):
        self.camera_id = camera_id
        self.stream_url = stream_url
        self.name = name or f"Camera_{camera_id[:8]}"
        self.is_active = False
        self.capture = None
        self.last_frame = None
        self.stats = {
            "frames_captured": 0,
            "detections_count": 0,
            "last_detection": None,
            "start_time": None,
            "errors": 0
        }
        self.config = {
            "models": ["intrusion", "people"],
            "confidence": 0.5,
            "iou_threshold": 0.45,
            "detection_interval": 2.0,  # Process every 2 seconds
            "alert_threshold": 1,  # Alert if 1+ objects detected
            "recording": False
        }
    
    def start(self):
        """Start camera capture"""
        try:
            self.capture = cv2.VideoCapture(self.stream_url)
            if not self.capture.isOpened():
                raise Exception(f"Failed to open camera stream: {self.stream_url}")
            
            # Set camera properties
            self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)  # Reduce buffer for real-time
            self.capture.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_active = True
            self.stats["start_time"] = datetime.now().isoformat()
            logger.info(f"Camera {self.name} started successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start camera {self.name}: {e}")
            self.stats["errors"] += 1
            return False
    
    def stop(self):
        """Stop camera capture"""
        self.is_active = False
        if self.capture:
            self.capture.release()
            self.capture = None
        logger.info(f"Camera {self.name} stopped")
    
    def capture_frame(self) -> Optional[str]:
        """Capture single frame as base64"""
        if not self.is_active or not self.capture:
            return None
        
        try:
            ret, frame = self.capture.read()
            if not ret:
                self.stats["errors"] += 1
                return None
            
            # Convert to base64
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            
            self.last_frame = frame_base64
            self.stats["frames_captured"] += 1
            
            return frame_base64
            
        except Exception as e:
            logger.error(f"Frame capture failed for {self.name}: {e}")
            self.stats["errors"] += 1
            return None
    
    def get_info(self) -> Dict:
        """Get camera information"""
        return {
            "camera_id": self.camera_id,
            "name": self.name,
            "stream_url": self.stream_url,
            "is_active": self.is_active,
            "config": self.config,
            "stats": self.stats
        }

class CCTVMonitoringService:
    """Service for CCTV monitoring and detection"""
    
    def __init__(self):
        self.cameras: Dict[str, CCTVCamera] = {}
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.alert_callbacks: List[Callable] = []
        self.detection_history: Dict[str, List] = {}
        self.is_monitoring = False
    
    def add_camera(self, stream_url: str, name: str = None, camera_id: str = None) -> str:
        """Add new IP camera"""
        if not camera_id:
            camera_id = str(uuid.uuid4())
        
        # Clean and validate stream URL
        original_url = stream_url.strip()
        
        # Remove fragments (anything after #)
        if '#' in original_url:
            original_url = original_url.split('#')[0]
            logger.info(f"Removed URL fragment, using: {original_url}")
        
        # Validate stream URL format
        parsed_url = urlparse(original_url)
        
        # Handle different URL types
        if original_url.isdigit():
            # USB camera (0, 1, 2, etc.)
            stream_url = int(original_url)
        elif parsed_url.scheme in ['rtsp', 'http', 'https']:
            # Direct stream URL
            stream_url = original_url
        elif parsed_url.scheme == '':
            # No scheme provided, try to determine best option
            if original_url.startswith('192.168.') or original_url.startswith('10.') or '.' in original_url:
                # Looks like IP address, assume RTSP
                stream_url = f"rtsp://{original_url}"
                logger.info(f"Assumed RTSP protocol: {stream_url}")
            else:
                # Keep as is and let OpenCV handle it
                stream_url = original_url
        else:
            # Unknown scheme, keep as is
            stream_url = original_url
        
        camera = CCTVCamera(camera_id, stream_url, name)
        self.cameras[camera_id] = camera
        self.detection_history[camera_id] = []
        
        logger.info(f"Camera added: {camera.name} ({camera_id}) with URL: {stream_url}")
        return camera_id
    
    def remove_camera(self, camera_id: str) -> bool:
        """Remove camera"""
        if camera_id not in self.cameras:
            return False
        
        # Stop monitoring if active
        self.stop_camera_monitoring(camera_id)
        
        # Remove camera
        camera = self.cameras[camera_id]
        camera.stop()
        del self.cameras[camera_id]
        del self.detection_history[camera_id]
        
        logger.info(f"Camera removed: {camera.name}")
        return True
    
    def get_camera(self, camera_id: str) -> Optional[CCTVCamera]:
        """Get camera by ID"""
        return self.cameras.get(camera_id)
    
    def list_cameras(self) -> List[Dict]:
        """List all cameras"""
        return [camera.get_info() for camera in self.cameras.values()]
    
    def update_camera_config(self, camera_id: str, config: Dict) -> bool:
        """Update camera configuration"""
        camera = self.get_camera(camera_id)
        if not camera:
            return False
        
        camera.config.update(config)
        return True
    
    async def start_camera_monitoring(self, camera_id: str) -> bool:
        """Start monitoring specific camera"""
        camera = self.get_camera(camera_id)
        if not camera:
            return False
        
        # Start camera
        if not camera.start():
            return False
        
        # Start monitoring task
        if camera_id not in self.monitoring_tasks:
            self.monitoring_tasks[camera_id] = asyncio.create_task(
                self._monitor_camera(camera_id)
            )
        
        return True
    
    def stop_camera_monitoring(self, camera_id: str):
        """Stop monitoring specific camera"""
        camera = self.get_camera(camera_id)
        if camera:
            camera.stop()
        
        # Cancel monitoring task
        if camera_id in self.monitoring_tasks:
            self.monitoring_tasks[camera_id].cancel()
            del self.monitoring_tasks[camera_id]
    
    async def start_all_monitoring(self):
        """Start monitoring all cameras"""
        self.is_monitoring = True
        
        for camera_id in self.cameras:
            await self.start_camera_monitoring(camera_id)
        
        logger.info("All camera monitoring started")
    
    def stop_all_monitoring(self):
        """Stop monitoring all cameras"""
        self.is_monitoring = False
        
        for camera_id in list(self.monitoring_tasks.keys()):
            self.stop_camera_monitoring(camera_id)
        
        logger.info("All camera monitoring stopped")
    
    async def _monitor_camera(self, camera_id: str):
        """Monitor single camera continuously"""
        camera = self.get_camera(camera_id)
        if not camera:
            return
        
        logger.info(f"Started monitoring camera: {camera.name}")
        
        while camera.is_active:
            try:
                # Capture frame
                frame_base64 = camera.capture_frame()
                if not frame_base64:
                    await asyncio.sleep(1)
                    continue
                
                # Process with configured models
                detection_results = {}
                total_detections = 0
                
                for model_type in camera.config["models"]:
                    try:
                        result = await yolo_service.detect_objects(
                            model_type=model_type,
                            image_data=frame_base64,
                            confidence=camera.config["confidence"],
                            iou_threshold=camera.config["iou_threshold"]
                        )
                        detection_results[model_type] = result
                        total_detections += result.get("total_detections", 0)
                        
                    except Exception as e:
                        logger.error(f"Detection failed for {camera.name} with {model_type}: {e}")
                        continue
                
                # Update camera stats
                if total_detections > 0:
                    camera.stats["detections_count"] += total_detections
                    camera.stats["last_detection"] = datetime.now().isoformat()
                
                # Save detection history
                if total_detections >= camera.config["alert_threshold"]:
                    detection_event = {
                        "timestamp": datetime.now().isoformat(),
                        "camera_id": camera_id,
                        "camera_name": camera.name,
                        "total_detections": total_detections,
                        "results": detection_results,
                        "frame_data": frame_base64 if camera.config.get("save_frames", False) else None
                    }
                    
                    self.detection_history[camera_id].append(detection_event)
                    
                    # Keep only last 100 events per camera
                    if len(self.detection_history[camera_id]) > 100:
                        self.detection_history[camera_id] = self.detection_history[camera_id][-100:]
                    
                    # Trigger alerts
                    await self._trigger_alert(detection_event)
                
                # Wait for next detection interval
                await asyncio.sleep(camera.config["detection_interval"])
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring error for {camera.name}: {e}")
                camera.stats["errors"] += 1
                await asyncio.sleep(5)  # Wait before retry
        
        logger.info(f"Stopped monitoring camera: {camera.name}")
    
    async def _trigger_alert(self, detection_event: Dict):
        """Trigger alert for detection event"""
        logger.warning(f"ALERT: Detection in {detection_event['camera_name']} - {detection_event['total_detections']} objects")
        
        # Call registered alert callbacks
        for callback in self.alert_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(detection_event)
                else:
                    callback(detection_event)
            except Exception as e:
                logger.error(f"Alert callback failed: {e}")
    
    def add_alert_callback(self, callback: Callable):
        """Add alert callback function"""
        self.alert_callbacks.append(callback)
    
    def get_detection_history(self, camera_id: str = None, limit: int = 50) -> List[Dict]:
        """Get detection history"""
        if camera_id:
            return self.detection_history.get(camera_id, [])[-limit:]
        else:
            # Return combined history from all cameras
            all_events = []
            for events in self.detection_history.values():
                all_events.extend(events)
            
            # Sort by timestamp and return latest
            all_events.sort(key=lambda x: x["timestamp"], reverse=True)
            return all_events[:limit]
    
    def get_system_status(self) -> Dict:
        """Get overall system status"""
        total_cameras = len(self.cameras)
        active_cameras = sum(1 for c in self.cameras.values() if c.is_active)
        total_detections = sum(c.stats["detections_count"] for c in self.cameras.values())
        
        return {
            "is_monitoring": self.is_monitoring,
            "total_cameras": total_cameras,
            "active_cameras": active_cameras,
            "total_detections": total_detections,
            "cameras": self.list_cameras()
        }

# Global service instance
cctv_service = CCTVMonitoringService()

# Example alert callback
async def default_alert_callback(detection_event: Dict):
    """Default alert callback - logs to console"""
    logger.warning(f"🚨 SECURITY ALERT: {detection_event['camera_name']} detected {detection_event['total_detections']} objects at {detection_event['timestamp']}")

# Register default callback
cctv_service.add_alert_callback(default_alert_callback)
