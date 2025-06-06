"""
WebSocket manager
The Scribe's Real-time Communication
"""

import json
import logging
from typing import Dict, List
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Dictionary to store active connections by session ID
        self.active_connections: Dict[str, List[WebSocket]] = {}
        logger.info("🔌 WebSocket manager initialized")
    
    async def connect(self, websocket: WebSocket, session_id: str):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        
        self.active_connections[session_id].append(websocket)
        logger.info(f"WebSocket connected for session {session_id}")
        
        # Send initial connection confirmation
        await self.send_personal_message({
            "type": "connection_established",
            "session_id": session_id,
            "message": "Connected to Aetherium session updates"
        }, websocket)
    
    async def disconnect(self, websocket: WebSocket, session_id: str):
        """Remove a WebSocket connection"""
        if session_id in self.active_connections:
            if websocket in self.active_connections[session_id]:
                self.active_connections[session_id].remove(websocket)
            
            # Clean up empty session lists
            if not self.active_connections[session_id]:
                del self.active_connections[session_id]
        
        logger.info(f"WebSocket disconnected for session {session_id}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific WebSocket connection"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending WebSocket message: {e}")
    
    async def broadcast_to_session(self, session_id: str, message: dict):
        """Broadcast a message to all connections for a specific session"""
        if session_id in self.active_connections:
            disconnected = []
            
            for websocket in self.active_connections[session_id]:
                try:
                    await websocket.send_text(json.dumps(message))
                except Exception as e:
                    logger.error(f"Error broadcasting to session {session_id}: {e}")
                    disconnected.append(websocket)
            
            # Remove disconnected websockets
            for websocket in disconnected:
                await self.disconnect(websocket, session_id)
    
    async def send_session_update(self, session_id: str, update_type: str, data: dict):
        """Send a session update to all connected clients"""
        message = {
            "type": "session_update",
            "session_id": session_id,
            "update_type": update_type,
            "data": data,
            "timestamp": data.get("timestamp", "")
        }
        
        await self.broadcast_to_session(session_id, message)
    
    async def send_call_status_update(self, session_id: str, status: str, details: dict = None):
        """Send call status update"""
        await self.send_session_update(session_id, "call_status", {
            "status": status,
            "details": details or {},
            "timestamp": details.get("timestamp", "") if details else ""
        })
    
    async def send_message_update(self, session_id: str, message_data: dict):
        """Send new message update"""
        await self.send_session_update(session_id, "new_message", message_data)
    
    async def send_workflow_update(self, session_id: str, workflow_state: dict):
        """Send workflow state update"""
        await self.send_session_update(session_id, "workflow_state", workflow_state)
    
    async def send_statistics_update(self, user_id: int, statistics: dict):
        """Send statistics update to all user sessions"""
        # Find all sessions for this user and broadcast
        message = {
            "type": "statistics_update",
            "user_id": user_id,
            "statistics": statistics
        }
        
        # This would need to be enhanced to track user sessions
        # For now, we'll broadcast to all active connections
        for session_id, connections in self.active_connections.items():
            await self.broadcast_to_session(session_id, message)
    
    def get_active_sessions(self) -> List[str]:
        """Get list of active session IDs"""
        return list(self.active_connections.keys())
    
    def get_connection_count(self, session_id: str = None) -> int:
        """Get number of active connections"""
        if session_id:
            return len(self.active_connections.get(session_id, []))
        else:
            return sum(len(connections) for connections in self.active_connections.values())