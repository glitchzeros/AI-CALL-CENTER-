"""
AI Usage Middleware
Middleware for tracking and enforcing AI call processing limits
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps

logger = logging.getLogger(__name__)

class AIUsageMiddleware:
    """Middleware for tracking AI usage and enforcing limits"""
    
    def __init__(self):
        self.active_sessions = {}  # Track active AI sessions
        
    async def start_ai_session(self, user_id: int, session_id: str, db_session) -> Dict[str, Any]:
        """
        Start tracking an AI session
        
        Args:
            user_id: User ID
            session_id: Unique session identifier
            db_session: Database session
            
        Returns:
            Dict with session info and whether it's allowed
        """
        try:
            from services.usage_tracking_service import UsageTrackingService
            usage_service = UsageTrackingService()
            
            # Check if user can start AI session (check for at least 1 minute)
            usage_check = await usage_service.check_ai_usage_limit(user_id, 1, db_session)
            
            if not usage_check["allowed"]:
                return {
                    "allowed": False,
                    "reason": usage_check["reason"],
                    "session_id": session_id
                }
            
            # Record session start
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
            logger.error(f"Error starting AI session: {e}")
            return {
                "allowed": False,
                "reason": f"Error checking usage limits: {str(e)}",
                "session_id": session_id
            }
    
    async def end_ai_session(self, session_id: str, db_session) -> Dict[str, Any]:
        """
        End an AI session and record usage
        
        Args:
            session_id: Session identifier
            db_session: Database session
            
        Returns:
            Dict with session summary
        """
        try:
            if session_id not in self.active_sessions:
                logger.warning(f"Attempted to end unknown session: {session_id}")
                return {"success": False, "reason": "Session not found"}
            
            session_info = self.active_sessions[session_id]
            end_time = datetime.utcnow()
            duration = end_time - session_info["start_time"]
            minutes_used = max(1, int(duration.total_seconds() / 60))  # Minimum 1 minute
            
            # Record usage
            from services.usage_tracking_service import UsageTrackingService
            usage_service = UsageTrackingService()
            
            success = await usage_service.record_ai_usage(
                user_id=session_info["user_id"],
                minutes_used=minutes_used,
                db=db_session
            )
            
            # Clean up session
            del self.active_sessions[session_id]
            
            logger.info(f"AI session ended: {session_id}, duration: {minutes_used} minutes")
            
            return {
                "success": success,
                "session_id": session_id,
                "duration_minutes": minutes_used,
                "user_id": session_info["user_id"]
            }
            
        except Exception as e:
            logger.error(f"Error ending AI session: {e}")
            return {
                "success": False,
                "reason": f"Error recording usage: {str(e)}",
                "session_id": session_id
            }
    
    async def check_session_limit(self, session_id: str, db_session) -> Dict[str, Any]:
        """
        Check if an active session is still within limits
        
        Args:
            session_id: Session identifier
            db_session: Database session
            
        Returns:
            Dict with limit check result
        """
        try:
            if session_id not in self.active_sessions:
                return {"allowed": False, "reason": "Session not found"}
            
            session_info = self.active_sessions[session_id]
            current_time = datetime.utcnow()
            duration = current_time - session_info["start_time"]
            current_minutes = int(duration.total_seconds() / 60)
            
            # Check current usage against limits
            from services.usage_tracking_service import UsageTrackingService
            usage_service = UsageTrackingService()
            
            usage_check = await usage_service.check_ai_usage_limit(
                session_info["user_id"], 
                current_minutes, 
                db_session
            )
            
            if not usage_check["allowed"]:
                # End session if limit exceeded
                await self.end_ai_session(session_id, db_session)
                return {
                    "allowed": False,
                    "reason": usage_check["reason"],
                    "session_ended": True
                }
            
            return {
                "allowed": True,
                "current_minutes": current_minutes,
                "remaining_minutes": usage_check.get("remaining_minutes", 0)
            }
            
        except Exception as e:
            logger.error(f"Error checking session limit: {e}")
            return {
                "allowed": False,
                "reason": f"Error checking limits: {str(e)}"
            }
    
    def get_active_sessions(self) -> Dict[str, Dict]:
        """Get all active sessions"""
        return self.active_sessions.copy()
    
    async def cleanup_expired_sessions(self, db_session, max_session_hours: int = 24):
        """
        Clean up sessions that have been active too long
        
        Args:
            db_session: Database session
            max_session_hours: Maximum hours a session can be active
        """
        try:
            current_time = datetime.utcnow()
            expired_sessions = []
            
            for session_id, session_info in self.active_sessions.items():
                duration = current_time - session_info["start_time"]
                if duration > timedelta(hours=max_session_hours):
                    expired_sessions.append(session_id)
            
            for session_id in expired_sessions:
                logger.warning(f"Cleaning up expired session: {session_id}")
                await self.end_ai_session(session_id, db_session)
                
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {e}")


# Global instance
ai_usage_middleware = AIUsageMiddleware()


def track_ai_usage(session_id_param: str = "session_id"):
    """
    Decorator to track AI usage for endpoints
    
    Args:
        session_id_param: Name of the parameter containing session ID
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract session_id from kwargs
            session_id = kwargs.get(session_id_param)
            if not session_id:
                logger.warning(f"No session_id found in {session_id_param}")
                return await func(*args, **kwargs)
            
            # Extract db_session (assuming it's in kwargs)
            db_session = kwargs.get("db") or kwargs.get("db_session")
            if not db_session:
                logger.warning("No database session found for AI usage tracking")
                return await func(*args, **kwargs)
            
            # Check session limits before processing
            limit_check = await ai_usage_middleware.check_session_limit(session_id, db_session)
            if not limit_check["allowed"]:
                from fastapi import HTTPException
                raise HTTPException(
                    status_code=429, 
                    detail=f"AI usage limit exceeded: {limit_check['reason']}"
                )
            
            # Execute the original function
            return await func(*args, **kwargs)
            
        return wrapper
    return decorator