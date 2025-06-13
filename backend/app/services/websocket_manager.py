"""
WebSocket connection manager for real-time updates.
"""

from fastapi import WebSocket
from typing import List, Dict, Set
import json
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and real-time messaging."""
    
    def __init__(self):
        # Store active connections
        self.active_connections: List[WebSocket] = []
        
        # Store subscriptions by channel
        self.subscriptions: Dict[str, Set[WebSocket]] = {}
        
        # Store connection metadata
        self.connection_metadata: Dict[WebSocket, Dict] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        self.active_connections.append(websocket)
        
        # Store connection metadata
        self.connection_metadata[websocket] = {
            'connected_at': datetime.utcnow(),
            'subscriptions': set(),
            'last_ping': datetime.utcnow()
        }
        
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")
        
        # Send welcome message
        await self.send_personal_message(websocket, {
            'type': 'connection_established',
            'message': 'Connected to EV Charging Analytics Platform',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        
        # Remove from all subscriptions
        if websocket in self.connection_metadata:
            subscriptions = self.connection_metadata[websocket].get('subscriptions', set())
            for channel in subscriptions:
                if channel in self.subscriptions:
                    self.subscriptions[channel].discard(websocket)
                    if not self.subscriptions[channel]:
                        del self.subscriptions[channel]
        
        # Remove metadata
        if websocket in self.connection_metadata:
            del self.connection_metadata[websocket]
        
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")
    
    async def send_personal_message(self, websocket: WebSocket, message: dict):
        """Send a message to a specific WebSocket connection."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected clients."""
        if not self.active_connections:
            return
        
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_to_channel(self, channel: str, message: dict):
        """Broadcast a message to all subscribers of a specific channel."""
        if channel not in self.subscriptions:
            return
        
        message_str = json.dumps(message)
        disconnected = []
        
        for connection in self.subscriptions[channel]:
            try:
                await connection.send_text(message_str)
            except Exception as e:
                logger.error(f"Error broadcasting to channel {channel}: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def subscribe(self, websocket: WebSocket, channel: str):
        """Subscribe a WebSocket connection to a channel."""
        if channel not in self.subscriptions:
            self.subscriptions[channel] = set()
        
        self.subscriptions[channel].add(websocket)
        
        # Update connection metadata
        if websocket in self.connection_metadata:
            self.connection_metadata[websocket]['subscriptions'].add(channel)
        
        logger.info(f"WebSocket subscribed to channel: {channel}")
        
        # Send confirmation
        await self.send_personal_message(websocket, {
            'type': 'subscription_confirmed',
            'channel': channel,
            'message': f'Subscribed to {channel}',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def unsubscribe(self, websocket: WebSocket, channel: str):
        """Unsubscribe a WebSocket connection from a channel."""
        if channel in self.subscriptions:
            self.subscriptions[channel].discard(websocket)
            if not self.subscriptions[channel]:
                del self.subscriptions[channel]
        
        # Update connection metadata
        if websocket in self.connection_metadata:
            self.connection_metadata[websocket]['subscriptions'].discard(channel)
        
        logger.info(f"WebSocket unsubscribed from channel: {channel}")
        
        # Send confirmation
        await self.send_personal_message(websocket, {
            'type': 'unsubscription_confirmed',
            'channel': channel,
            'message': f'Unsubscribed from {channel}',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    async def send_realtime_metrics(self, metrics: dict):
        """Send real-time metrics to subscribers."""
        message = {
            'type': 'realtime_metrics',
            'data': metrics,
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.broadcast_to_channel('realtime_metrics', message)
    
    async def send_data_update(self, update_type: str, data: dict):
        """Send data update notification."""
        message = {
            'type': 'data_update',
            'update_type': update_type,
            'data': data,
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.broadcast_to_channel('data_updates', message)
    
    async def send_model_update(self, model_name: str, status: str, details: dict = None):
        """Send ML model update notification."""
        message = {
            'type': 'model_update',
            'model_name': model_name,
            'status': status,
            'details': details or {},
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.broadcast_to_channel('model_updates', message)
    
    async def send_alert(self, alert_type: str, message: str, severity: str = 'info'):
        """Send alert notification."""
        alert_message = {
            'type': 'alert',
            'alert_type': alert_type,
            'message': message,
            'severity': severity,
            'timestamp': datetime.utcnow().isoformat()
        }
        await self.broadcast(alert_message)
    
    async def ping_connections(self):
        """Send ping to all connections to keep them alive."""
        ping_message = {
            'type': 'ping',
            'timestamp': datetime.utcnow().isoformat()
        }
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(ping_message))
                # Update last ping time
                if connection in self.connection_metadata:
                    self.connection_metadata[connection]['last_ping'] = datetime.utcnow()
            except Exception as e:
                logger.error(f"Error pinging connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    def get_connection_stats(self) -> dict:
        """Get statistics about WebSocket connections."""
        channel_stats = {}
        for channel, connections in self.subscriptions.items():
            channel_stats[channel] = len(connections)
        
        return {
            'total_connections': len(self.active_connections),
            'channels': channel_stats,
            'connection_details': [
                {
                    'connected_at': metadata['connected_at'].isoformat(),
                    'subscriptions': list(metadata['subscriptions']),
                    'last_ping': metadata['last_ping'].isoformat()
                }
                for metadata in self.connection_metadata.values()
            ]
        }
    
    async def cleanup_stale_connections(self, max_age_minutes: int = 60):
        """Clean up connections that haven't been active recently."""
        cutoff_time = datetime.utcnow().timestamp() - (max_age_minutes * 60)
        stale_connections = []
        
        for connection, metadata in self.connection_metadata.items():
            if metadata['last_ping'].timestamp() < cutoff_time:
                stale_connections.append(connection)
        
        for connection in stale_connections:
            logger.info("Cleaning up stale WebSocket connection")
            self.disconnect(connection)
            try:
                await connection.close()
            except:
                pass  # Connection might already be closed


# Background task to send periodic updates
async def websocket_background_task(manager: WebSocketManager):
    """Background task for WebSocket maintenance and updates."""
    while True:
        try:
            # Send ping every 30 seconds
            await manager.ping_connections()
            
            # Clean up stale connections every 5 minutes
            await manager.cleanup_stale_connections()
            
            # Send sample real-time metrics (in a real app, this would come from actual data)
            sample_metrics = {
                'active_sessions': 127,
                'avg_duration': '2.3h',
                'current_cost': '$0.28/kWh',
                'network_health': '98.5%'
            }
            await manager.send_realtime_metrics(sample_metrics)
            
            await asyncio.sleep(30)  # Wait 30 seconds
            
        except Exception as e:
            logger.error(f"Error in WebSocket background task: {e}")
            await asyncio.sleep(30)
