"""
AI Usage Middleware
Middleware for tracking and enforcing AI call processing limits
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps
from sqlalchemy.orm import sessionmaker
from database.connection import AsyncSessionLocal, Base
from sqlalchemy import Column, Integer, Date, ForeignKey, DateTime
from sqlalchemy.sql import func

logger = logging.getLogger(__name__)

# Define the model at the module level for correct registration
class UserDailyUsage(Base):
    __tablename__ = "user_daily_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    usage_date = Column(Date, nullable=False)
    ai_minutes_used = Column(Integer, default=0)
    sms_count_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class AIUsageMiddleware:
    """Middleware for tracking AI usage and enforcing limits"""
    
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}  # Track active AI sessions
        
    async def start_ai_session(self, user_id: int, session_id: str, db_session) -> Dict[str, Any]:
        """
        Start tracking an AI session
        """
        try:
            from services.usage_tracking_service import UsageTrackingService
            usage_service = UsageTrackingService()
            
            usage_check = await usage_service.check_ai_usage_limit(user_id, 1, db_session)
            
            if not usage_check["allowed"]:
                return {
                    "allowed": False,
                    "reason": usage_check["reason"],
                    "session_id": session_id
                }
            
            self.active_sessions[session_id] = {
                "user_id": user_id,
                "start_time": datetime.utcnow(),
                "total_minutes": 0
            }
            
            logger.info(f"AI session started for user {user_id}, session {session_id}")
            
            return {
                "allowed": True,
                "session_id": session_id,
                "remaining_minutes": usage_check.get("remaining_minutes", 0)
            }
            
        except Exception as e:
            logger.error(f"Error starting AI session: {e}", exc_info=True)
            return {"allowed": False, "reason": "Error checking usage limits", "session_id": session_id}
    
    async def end_ai_session(self, session_id: str, db_session) -> Dict[str, Any]:
        """
        End an AI session and record usage
        """
        try:
            if session_id not in self.active_sessions:
                logger.warning(f"Attempted to end unknown session: {session_id}")
                return {"success": False, "reason": "Session not found", "session_id": session_id}
            
            session_info = self.active_sessions.pop(session_id)
            end_time = datetime.utcnow()
            duration = end_time - session_info["start_time"]
            minutes_used = max(1, int(duration.total_seconds() / 60))
            
            from services.usage_tracking_service import UsageTrackingService
            usage_service = UsageTrackingService()
            
            success = await usage_service.record_ai_usage(
                user_id=session_info["user_id"],
                minutes_used=minutes_used,
                db=db_session
            )
            
            logger.info(f"AI session ended: {session_id}, duration: {minutes_used} minutes")
            
            return {
                "success": success,
                "session_id": session_id,
                "duration_minutes": minutes_used,
                "user_id": session_info["user_id"]
            }
            
        except Exception as e:
            logger.error(f"Error ending AI session: {e}", exc_info=True)
            return {"success": False, "reason": "Error recording usage", "session_id": session_id}
    
    async def check_session_limit(self, session_id: str, db_session) -> Dict[str, Any]:
        """
        Check if an active session is still within limits
        """
        try:
            if session_id not in self.active_sessions:
                return {"allowed": False, "reason": "Session not found", "session_id": session_id}
            
            session_info = self.active_sessions[session_id]
            duration = datetime.utcnow() - session_info["start_time"]
            current_minutes = int(duration.total_seconds() / 60)
            
            from services.usage_tracking_service import UsageTrackingService
            usage_service = UsageTrackingService()
            
            usage_check = await usage_service.check_ai_usage_limit(
                session_info["user_id"], 
                current_minutes, 
                db_session
            )
            
            if not usage_check["allowed"]:
                await self.end_ai_session(session_id, db_session)
                return {"allowed": False, "reason": usage_check["reason"], "session_ended": True}
            
            return {"allowed": True, "current_minutes": current_minutes, "remaining_minutes": usage_check.get("remaining_minutes", 0)}
            
        except Exception as e:
            logger.error(f"Error checking session limit: {e}", exc_info=True)
            return {"allowed": False, "reason": "Error checking limits"}
    
    def get_active_sessions(self) -> Dict[str, Dict]:
        """Get all active sessions"""
        return self.active_sessions.copy()
    
    async def cleanup_expired_sessions(self, db_session, max_session_hours: int = 24):
        """
        Clean up sessions that have been active too long
        """
        try:
            now = datetime.utcnow()
            expired_sessions = [
                sid for sid, info in self.active_sessions.items()
                if now - info["start_time"] > timedelta(hours=max_session_hours)
            ]
            
            for session_id in expired_sessions:
                logger.warning(f"Cleaning up expired session: {session_id}")
                await self.end_ai_session(session_id, db_session)
                
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}", exc_info=True)

# Global instance
ai_usage_middleware = AIUsageMiddleware()
