"""
Optimized Universal YOLO Models Service
Supports: intrusion, people, security_threats, vehicle detection
High-performance implementation with caching, parallel processing, and monitoring
"""
import os
import base64
import time
import asyncio
from io import BytesIO
import numpy as np
from PIL import Image
from typing import List, Dict, Any, Optional
from fastapi import HTTPException
import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# Import YOLO dependencies
try:
    from ultralytics import YOLO
    import torch
    YOLO_AVAILABLE = True
    # Check GPU availability
    GPU_AVAILABLE = torch.cuda.is_available()
    DEVICE = "cuda" if GPU_AVAILABLE else "cpu"
except ImportError:
    YOLO_AVAILABLE = False
    GPU_AVAILABLE = False
    DEVICE = "cpu"
    print("Warning: YOLO dependencies not available")

# Import database functions with fallback
try:
    from app.models.models import save_detection_result, get_detection_history, update_model_metadata
    DATABASE_AVAILABLE = True
except ImportError:
    DATABASE_AVAILABLE = False
    # Create dummy functions for graceful fallback
    async def save_detection_result(*args, **kwargs):
        pass
    async def get_detection_history(*args, **kwargs):
        return []
    async def update_model_metadata(*args, **kwargs):
        pass

logger = logging.getLogger(__name__)

class OptimizedYOLOService:
    """High-performance YOLO service with optimization for surveillance systems"""
    
    def __init__(self):
        self.models = {}  # Cache for loaded models
        self.model_configs = {
            "intrusion": {
                "file": "intrusion_yolov11.pt",
                "classes": ["person", "intrusion"],
                "priority": "high"  # High priority for security
            },
            "people": {
                "file": "People_yolov8s_trained.pt", 
                "classes": ["person"],
                "priority": "high"
            },
            "security_threats": {
                "file": "SecurityThreats_best_gun.pt",
                "classes": ["gun", "knife", "weapon"],
                "priority": "critical"  # Critical for security
            },
            "vehicle": {
                "file": "vehicle_model_v11.pt",
                "classes": ["car", "truck", "bus", "motorcycle"],
                "priority": "medium"
            }
        }
        
        # Performance tracking
        self.stats = {
            "total_detections": 0,
            "total_processing_time": 0.0,
            "model_usage": {model: 0 for model in self.model_configs.keys()},
            "error_count": 0,
            "cache_hits": 0,
            "start_time": datetime.now()
        }
        
        # Thread pool for CPU-intensive operations
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
        # Image preprocessing cache
        self.image_cache = {}
        self.cache_max_size = 100
        
        # Use absolute path to models
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.models_path = os.path.join(os.path.dirname(current_dir), "yolo_models")
        
        logger.info(f"YOLO Service initialized - GPU: {GPU_AVAILABLE}, Device: {DEVICE}")
    
    def _get_model_path(self, model_type: str) -> str:
        """Get full path to model file"""
        config = self.model_configs.get(model_type)
        if not config:
            raise ValueError(f"Unknown model type: {model_type}")
        
        return os.path.join(self.models_path, config["file"])
    
    async def load_model(self, model_type: str) -> bool:
        """Optimized model loading with caching and GPU support"""
        try:
            if not YOLO_AVAILABLE:
                raise ImportError("YOLO dependencies not available")
            
            if model_type in self.models:
                logger.info(f"Model {model_type} already loaded")
                return True
            
            model_path = self._get_model_path(model_type)
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model file not found: {model_path}")
            
            # Load model with optimization
            start_time = time.time()
            model = YOLO(model_path)
            
            # Set device for GPU acceleration
            if GPU_AVAILABLE:
                model.to(DEVICE)
                logger.info(f"Model {model_type} loaded on GPU")
            else:
                logger.info(f"Model {model_type} loaded on CPU")
            
            # Warm up model with dummy inference
            if GPU_AVAILABLE:
                dummy_image = Image.new('RGB', (640, 640), color='black')
                _ = model(dummy_image, verbose=False)
                logger.info(f"Model {model_type} warmed up")
            
            self.models[model_type] = model
            load_time = time.time() - start_time
            
            # Get actual class names from model
            if hasattr(model, 'names'):
                classes = list(model.names.values())
                self.model_configs[model_type]["classes"] = classes
                
                # Update database metadata (optional - silent fail if DB unavailable)
                if DATABASE_AVAILABLE:
                    try:
                        await update_model_metadata(model_type, self.model_configs[model_type]["file"], classes)
                    except Exception as db_error:
                        logger.debug(f"Database metadata update skipped for {model_type}: {db_error}")
                        pass
            
            logger.info(f"Model {model_type} loaded successfully in {load_time:.2f}s")
            return True
            
        except Exception as e:
            logger.error(f"Error loading model {model_type}: {str(e)}")
            self.stats["error_count"] += 1
            return False
    
    def _decode_image_optimized(self, image_data: str) -> tuple[Image.Image, str]:
        """Optimized image decoding with caching - returns image and cache_key"""
        try:
            # Create cache key
            cache_key = hash(image_data[:100])  # Use first 100 chars as key
            
            # Check cache first
            if cache_key in self.image_cache:
                self.stats["cache_hits"] += 1
                return self.image_cache[cache_key].copy(), str(cache_key)
            
            # Remove data URL prefix if present
            if image_data.startswith('data:image'):
                image_data = image_data.split(',')[1]
            
            # Decode base64
            image_bytes = base64.b64decode(image_data)
            image = Image.open(BytesIO(image_bytes))
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Cache management
            if len(self.image_cache) >= self.cache_max_size:
                # Remove oldest entry (simple FIFO)
                oldest_key = next(iter(self.image_cache))
                del self.image_cache[oldest_key]
            
            # Cache the image
            self.image_cache[cache_key] = image.copy()
            
            return image, str(cache_key)
            
        except Exception as e:
            raise ValueError(f"Invalid image data: {str(e)}")
    
    async def detect_objects_optimized(self, model_type: str, image_data: str, 
                                     confidence: float = 0.5, iou_threshold: float = 0.45) -> Dict[str, Any]:
        """Optimized object detection with performance monitoring"""
        try:
            overall_start = time.time()
            
            # Load model if not loaded
            if model_type not in self.models:
                success = await self.load_model(model_type)
                if not success:
                    raise HTTPException(status_code=500, detail=f"Failed to load model: {model_type}")
            
            model = self.models[model_type]
            
            # Decode image (optimized with caching)
            decode_start = time.time()
            image, cache_key = self._decode_image_optimized(image_data)
            decode_time = time.time() - decode_start
            
            image_size = [image.width, image.height]
            
            # Run inference in thread pool to avoid blocking
            inference_start = time.time()
            
            def run_inference():
                return model(image, conf=confidence, iou=iou_threshold, verbose=False)
            
            # Use thread pool for CPU-intensive inference
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(self.thread_pool, run_inference)
            
            inference_time = time.time() - inference_start
            
            # Process results (optimized)
            process_start = time.time()
            detections = []
            
            if results and len(results) > 0:
                result = results[0]
                if hasattr(result, 'boxes') and result.boxes is not None:
                    boxes = result.boxes
                    
                    # Vectorized processing for better performance
                    if len(boxes) > 0:
                        box_coords = boxes.xyxy.cpu().numpy()
                        confidences = boxes.conf.cpu().numpy()
                        class_ids = boxes.cls.cpu().numpy().astype(int)
                        
                        for i in range(len(boxes)):
                            # Get class name
                            cls_id = class_ids[i]
                            class_name = model.names[cls_id] if hasattr(model, 'names') else f"class_{cls_id}"
                            
                            detection = {
                                "class_id": int(cls_id),
                                "class_name": class_name,
                                "confidence": float(confidences[i]),
                                "bbox": box_coords[i].tolist(),
                                "center": [
                                    float((box_coords[i][0] + box_coords[i][2]) / 2),
                                    float((box_coords[i][1] + box_coords[i][3]) / 2)
                                ],
                                "area": float((box_coords[i][2] - box_coords[i][0]) * (box_coords[i][3] - box_coords[i][1]))
                            }
                            detections.append(detection)
            
            process_time = time.time() - process_start
            total_time = time.time() - overall_start
            
            # Update statistics
            self.stats["total_detections"] += 1
            self.stats["total_processing_time"] += total_time
            self.stats["model_usage"][model_type] += 1
            
            # Save to database (optional - silent fail if DB unavailable)
            if DATABASE_AVAILABLE:
                try:
                    await save_detection_result(
                        model_type=model_type,
                        detections=detections,
                        processing_time=total_time,
                        confidence=confidence,
                        iou=iou_threshold,
                        image_size=image_size
                    )
                except Exception as db_error:
                    logger.debug(f"Database save skipped for {model_type}: {db_error}")
                    pass
            
            return {
                "success": True,
                "model_type": model_type,
                "detections": detections,
                "total_detections": len(detections),
                "processing_time": total_time,
                "performance_breakdown": {
                    "decode_time": decode_time,
                    "inference_time": inference_time,
                    "process_time": process_time,
                    "total_time": total_time
                },
                "image_size": image_size,
                "device": DEVICE,
                "cached": cache_key in self.image_cache
            }
            
        except Exception as e:
            self.stats["error_count"] += 1
            logger.error(f"Error in optimized object detection: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Detection failed: {str(e)}")
    
    # Keep the original method for backward compatibility
    async def detect_objects(self, model_type: str, image_data: str, 
                           confidence: float = 0.5, iou_threshold: float = 0.45) -> Dict[str, Any]:
        """Original detection method - calls optimized version"""
        return await self.detect_objects_optimized(model_type, image_data, confidence, iou_threshold)
    
    async def get_model_info(self, model_type: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        try:
            config = self.model_configs.get(model_type)
            if not config:
                raise ValueError(f"Unknown model type: {model_type}")
            
            return {
                "model_type": model_type,
                "model_file": config["file"],
                "classes": config["classes"],
                "loaded": model_type in self.models,
                "path": self._get_model_path(model_type)
            }
            
        except Exception as e:
            logger.error(f"Error getting model info: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def list_all_models(self) -> Dict[str, Any]:
        """List all available models"""
        try:
            models_info = []
            for model_type in self.model_configs.keys():
                info = await self.get_model_info(model_type)
                models_info.append(info)
            
            return {
                "success": True,
                "models": models_info,
                "total_models": len(models_info)
            }
            
        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def get_detection_history(self, model_type: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get detection history from database"""
        try:
            history = await get_detection_history(model_type, limit)
            return history
            
        except Exception as e:
            logger.error(f"Error getting detection history: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

    async def get_service_stats(self) -> Dict[str, Any]:
        """Get comprehensive service statistics"""
        uptime = (datetime.now() - self.stats["start_time"]).total_seconds()
        avg_processing_time = (
            self.stats["total_processing_time"] / max(1, self.stats["total_detections"])
        )
        
        return {
            "service_info": {
                "gpu_available": GPU_AVAILABLE,
                "device": DEVICE,
                "models_loaded": len(self.models),
                "cache_size": len(self.image_cache),
                "thread_pool_size": self.thread_pool._max_workers
            },
            "performance": {
                "total_detections": self.stats["total_detections"],
                "total_processing_time": self.stats["total_processing_time"],
                "average_processing_time": avg_processing_time,
                "cache_hits": self.stats["cache_hits"],
                "error_count": self.stats["error_count"],
                "uptime_seconds": uptime
            },
            "model_usage": self.stats["model_usage"],
            "loaded_models": list(self.models.keys())
        }
    
    async def preload_all_models(self):
        """Preload all models for better performance"""
        logger.info("Preloading all YOLO models...")
        for model_type in self.model_configs.keys():
            try:
                await self.load_model(model_type)
                logger.info(f"✅ {model_type} model preloaded")
            except Exception as e:
                logger.error(f"❌ Failed to preload {model_type}: {e}")
        
        logger.info(f"Preloading complete. {len(self.models)}/{len(self.model_configs)} models loaded.")
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "checks": {}
        }
        
        # Check YOLO availability
        health_status["checks"]["yolo_available"] = YOLO_AVAILABLE
        
        # Check GPU availability
        health_status["checks"]["gpu_available"] = GPU_AVAILABLE
        
        # Check models
        health_status["checks"]["models_loaded"] = len(self.models)
        health_status["checks"]["models_expected"] = len(self.model_configs)
        
        # Check database
        health_status["checks"]["database_available"] = DATABASE_AVAILABLE
        
        # Overall health
        critical_checks = [
            YOLO_AVAILABLE,
            len(self.models) > 0
        ]
        
        if not all(critical_checks):
            health_status["status"] = "degraded"
        
        if self.stats["error_count"] > 100:  # Too many errors
            health_status["status"] = "unhealthy"
        
        return health_status

# Global service instance
yolo_service = OptimizedYOLOService()
