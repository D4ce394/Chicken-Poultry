"""
Monitoring Service for AI-FRSS System
Handles real-time monitoring functionality including statistics and alerts
"""

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import asyncio
import json
from app.services.database_service import DatabaseService
try:
    from app.services.models_service import OptimizedYOLOService
except Exception as e:
    print(f"Warning: YOLO not available for monitoring: {e}")
    OptimizedYOLOService = object

class MonitoringService:
    def __init__(self, db_service: DatabaseService, yolo_service: OptimizedYOLOService):
        self.db_service = db_service
        self.yolo_service = yolo_service
        self.active_connections: Dict[str, Any] = {}
        self.monitoring_active = False
        
    async def start_monitoring(self, connection_id: str):
        """Start monitoring for a specific connection"""
        self.active_connections[connection_id] = {
            'started_at': datetime.now(),
            'last_update': datetime.now()
        }
        self.monitoring_active = True
        
    async def stop_monitoring(self, connection_id: str):
        """Stop monitoring for a specific connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        if not self.active_connections:
            self.monitoring_active = False
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get current system statistics"""
        try:
            # Get basic statistics from database
            stats = await self.db_service.execute_query(
                "SELECT COUNT(*) as total_detections FROM detections WHERE DATE(created_at) = DATE('now')"
            )
            
            today_detections = stats[0]['total_detections'] if stats else 0
            
            # Get detection counts by type today
            detection_types = await self.db_service.execute_query(
                """SELECT detection_type, COUNT(*) as count 
                   FROM detections 
                   WHERE DATE(created_at) = DATE('now') 
                   GROUP BY detection_type"""
            )
            
            # Get active alerts
            active_alerts = await self.db_service.execute_query(
                "SELECT COUNT(*) as count FROM alerts WHERE status = 'active'"
            )
            
            # Get recent activities (last 10)
            recent_activities = await self.db_service.execute_query(
                """SELECT detection_type, confidence, created_at 
                   FROM detections 
                   ORDER BY created_at DESC 
                   LIMIT 10"""
            )
            
            return {
                'system_status': 'active' if self.monitoring_active else 'inactive',
                'active_connections': len(self.active_connections),
                'today_detections': today_detections,
                'active_alerts': active_alerts[0]['count'] if active_alerts else 0,
                'detection_breakdown': {item['detection_type']: item['count'] for item in detection_types},
                'recent_activities': recent_activities,
                'yolo_models_status': await self.yolo_service.get_service_stats(),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting system stats: {e}")
            return {
                'system_status': 'error',
                'error': str(e),
                'last_updated': datetime.now().isoformat()
            }
    
    async def get_detection_statistics(self, days: int = 7) -> Dict[str, Any]:
        """Get detection statistics for the specified number of days"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Daily detection counts
            daily_stats = await self.db_service.execute_query(
                """SELECT DATE(created_at) as date, COUNT(*) as count,
                          detection_type
                   FROM detections 
                   WHERE created_at >= ? 
                   GROUP BY DATE(created_at), detection_type
                   ORDER BY date DESC""",
                (start_date.isoformat(),)
            )
            
            # Hourly distribution for today
            hourly_stats = await self.db_service.execute_query(
                """SELECT strftime('%H', created_at) as hour, COUNT(*) as count
                   FROM detections 
                   WHERE DATE(created_at) = DATE('now')
                   GROUP BY hour
                   ORDER BY hour"""
            )
            
            # Top detection types
            top_detections = await self.db_service.execute_query(
                """SELECT detection_type, COUNT(*) as count,
                          AVG(confidence) as avg_confidence
                   FROM detections 
                   WHERE created_at >= ? 
                   GROUP BY detection_type
                   ORDER BY count DESC
                   LIMIT 10""",
                (start_date.isoformat(),)
            )
            
            return {
                'period': f'{days} days',
                'daily_statistics': daily_stats,
                'hourly_distribution': hourly_stats,
                'top_detections': top_detections,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting detection statistics: {e}")
            return {'error': str(e)}
    
    async def get_alerts_summary(self) -> Dict[str, Any]:
        """Get summary of alerts"""
        try:
            # Active alerts
            active_alerts = await self.db_service.execute_query(
                """SELECT id, alert_type, message, priority, created_at
                   FROM alerts 
                   WHERE status = 'active'
                   ORDER BY priority DESC, created_at DESC"""
            )
            
            # Recent resolved alerts
            resolved_alerts = await self.db_service.execute_query(
                """SELECT id, alert_type, message, priority, created_at, resolved_at
                   FROM alerts 
                   WHERE status = 'resolved'
                   ORDER BY resolved_at DESC
                   LIMIT 5"""
            )
            
            # Alert statistics
            alert_stats = await self.db_service.execute_query(
                """SELECT alert_type, COUNT(*) as count, priority
                   FROM alerts 
                   WHERE DATE(created_at) = DATE('now')
                   GROUP BY alert_type, priority"""
            )
            
            return {
                'active_alerts': active_alerts,
                'recent_resolved': resolved_alerts,
                'today_statistics': alert_stats,
                'total_active': len(active_alerts),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error getting alerts summary: {e}")
            return {'error': str(e)}
    
    async def process_detection_result(self, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """Process detection result and create alerts if necessary"""
        try:
            detection_type = detection_result.get('detection_type')
            confidence = detection_result.get('confidence', 0)
            
            # Store detection in database
            await self.db_service.execute_query(
                """INSERT INTO detections (detection_type, confidence, details, created_at)
                   VALUES (?, ?, ?, ?)""",
                (detection_type, confidence, json.dumps(detection_result), datetime.now().isoformat())
            )
            
            # Check if alert should be created based on detection type and confidence
            should_alert = await self._should_create_alert(detection_type, confidence)
            
            if should_alert:
                alert_data = await self._create_alert_from_detection(detection_result)
                return {
                    'detection_stored': True,
                    'alert_created': True,
                    'alert_data': alert_data
                }
            
            return {
                'detection_stored': True,
                'alert_created': False
            }
            
        except Exception as e:
            print(f"Error processing detection result: {e}")
            return {'error': str(e)}
    
    async def _should_create_alert(self, detection_type: str, confidence: float) -> bool:
        """Determine if an alert should be created based on detection"""
        # Define alert thresholds for different detection types
        alert_thresholds = {
            'intrusion': 0.7,
            'security_threats': 0.6,
            'people': 0.8,
            'vehicle': 0.75
        }
        
        threshold = alert_thresholds.get(detection_type, 0.8)
        return confidence >= threshold
    
    async def _create_alert_from_detection(self, detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """Create an alert based on detection result"""
        try:
            detection_type = detection_result.get('detection_type')
            confidence = detection_result.get('confidence', 0)
            
            # Determine alert priority and message
            priority_map = {
                'intrusion': 'high',
                'security_threats': 'critical',
                'people': 'medium',
                'vehicle': 'low'
            }
            
            message_map = {
                'intrusion': f'Intrusion detected with {confidence:.2%} confidence',
                'security_threats': f'Security threat detected with {confidence:.2%} confidence',
                'people': f'Person detected with {confidence:.2%} confidence',
                'vehicle': f'Vehicle detected with {confidence:.2%} confidence'
            }
            
            priority = priority_map.get(detection_type, 'medium')
            message = message_map.get(detection_type, f'{detection_type} detected')
            
            # Insert alert into database
            await self.db_service.execute_query(
                """INSERT INTO alerts (alert_type, message, priority, status, details, created_at)
                   VALUES (?, ?, ?, 'active', ?, ?)""",
                (detection_type, message, priority, json.dumps(detection_result), datetime.now().isoformat())
            )
            
            return {
                'alert_type': detection_type,
                'message': message,
                'priority': priority,
                'confidence': confidence,
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error creating alert: {e}")
            return {'error': str(e)}
    
    async def get_live_monitoring_data(self) -> Dict[str, Any]:
        """Get live monitoring data for real-time updates"""
        try:
            system_stats = await self.get_system_stats()
            alerts_summary = await self.get_alerts_summary()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'system_stats': system_stats,
                'alerts_summary': alerts_summary,
                'monitoring_status': 'active' if self.monitoring_active else 'inactive'
            }
            
        except Exception as e:
            print(f"Error getting live monitoring data: {e}")
            return {'error': str(e)}


# WebSocket event handler function
async def handle_monitoring_ws_event(websocket, event_data: dict, db_service: DatabaseService, yolo_service: OptimizedYOLOService):
    """Handle WebSocket events for monitoring"""
    try:
        event_type = event_data.get('type')
        
        # Initialize monitoring service
        monitoring_service = MonitoringService(db_service, yolo_service)
        
        if event_type == 'start_monitoring':
            connection_id = event_data.get('connection_id', 'unknown')
            await monitoring_service.start_monitoring(connection_id)
            
            # Send initial system stats
            stats = await monitoring_service.get_system_stats()
            await websocket.send_json({
                'type': 'monitoring_started',
                'data': stats
            })
            
        elif event_type == 'stop_monitoring':
            connection_id = event_data.get('connection_id', 'unknown')
            await monitoring_service.stop_monitoring(connection_id)
            
            await websocket.send_json({
                'type': 'monitoring_stopped',
                'message': 'Monitoring stopped successfully'
            })
            
        elif event_type == 'get_stats':
            stats = await monitoring_service.get_system_stats()
            await websocket.send_json({
                'type': 'system_stats',
                'data': stats
            })
            
        elif event_type == 'get_detection_stats':
            days = event_data.get('days', 7)
            stats = await monitoring_service.get_detection_statistics(days)
            await websocket.send_json({
                'type': 'detection_statistics',
                'data': stats
            })
            
        elif event_type == 'get_alerts':
            alerts = await monitoring_service.get_alerts_summary()
            await websocket.send_json({
                'type': 'alerts_summary',
                'data': alerts
            })
            
        elif event_type == 'get_live_data':
            live_data = await monitoring_service.get_live_monitoring_data()
            await websocket.send_json({
                'type': 'live_monitoring_data',
                'data': live_data
            })
            
        else:
            await websocket.send_json({
                'type': 'error',
                'message': f'Unknown event type: {event_type}'
            })
            
    except Exception as e:
        print(f"Error handling monitoring WebSocket event: {e}")
        await websocket.send_json({
            'type': 'error',
            'message': f'Error processing request: {str(e)}'
        })
