"""
AI Sessions router
Manages AI call processing sessions and usage tracking
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
import uuid

from database.connection import get_database
from models.user import User
from routers.auth import get_current_user
from services.ai_usage_middleware import ai_usage_middleware

router = APIRouter()

class StartAISessionRequest(BaseModel):
    session_type: str = "call_processing"
    metadata: Optional[dict] = None

class StartAISessionResponse(BaseModel):
    allowed: bool
    session_id: Optional[str] = None
    reason: Optional[str] = None
    remaining_minutes: Optional[int] = None

class EndAISessionRequest(BaseModel):
    session_id: str

class EndAISessionResponse(BaseModel):
    success: bool
    session_id: str
    duration_minutes: Optional[int] = None
    reason: Optional[str] = None

class SessionStatusResponse(BaseModel):
    allowed: bool
    session_id: str
    current_minutes: Optional[int] = None
    remaining_minutes: Optional[int] = None
    reason: Optional[str] = None
    session_ended: Optional[bool] = None

@router.post("/start", response_model=StartAISessionResponse)
async def start_ai_session(
    request: StartAISessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Start an AI processing session
    The Scribe's AI Session Initiation
    """
    try:
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Start AI session with usage tracking
        result = await ai_usage_middleware.start_ai_session(
            user_id=current_user.id,
            session_id=session_id,
            db_session=db
        )
        
        return StartAISessionResponse(
            allowed=result["allowed"],
            session_id=result.get("session_id"),
            reason=result.get("reason"),
            remaining_minutes=result.get("remaining_minutes")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start AI session: {str(e)}")

@router.post("/end", response_model=EndAISessionResponse)
async def end_ai_session(
    request: EndAISessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    End an AI processing session
    The Scribe's AI Session Conclusion
    """
    try:
        result = await ai_usage_middleware.end_ai_session(
            session_id=request.session_id,
            db_session=db
        )
        
        return EndAISessionResponse(
            success=result["success"],
            session_id=result["session_id"],
            duration_minutes=result.get("duration_minutes"),
            reason=result.get("reason")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to end AI session: {str(e)}")

@router.get("/status/{session_id}", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Check AI session status and limits
    The Scribe's AI Session Monitor
    """
    try:
        result = await ai_usage_middleware.check_session_limit(
            session_id=session_id,
            db_session=db
        )
        
        return SessionStatusResponse(
            allowed=result["allowed"],
            session_id=session_id,
            current_minutes=result.get("current_minutes"),
            remaining_minutes=result.get("remaining_minutes"),
            reason=result.get("reason"),
            session_ended=result.get("session_ended")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to check session status: {str(e)}")

@router.get("/active")
async def get_active_sessions(
    current_user: User = Depends(get_current_user)
):
    """
    Get all active AI sessions for debugging
    The Scribe's Active Session Registry
    """
    try:
        active_sessions = ai_usage_middleware.get_active_sessions()
        
        # Filter sessions for current user
        user_sessions = {
            session_id: session_info 
            for session_id, session_info in active_sessions.items()
            if session_info["user_id"] == current_user.id
        }
        
        return {
            "active_sessions": user_sessions,
            "total_count": len(user_sessions)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get active sessions: {str(e)}")

@router.post("/cleanup")
async def cleanup_expired_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Clean up expired AI sessions
    The Scribe's Session Cleanup
    """
    try:
        await ai_usage_middleware.cleanup_expired_sessions(db)
        
        return {
            "success": True,
            "message": "Expired sessions cleaned up"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup sessions: {str(e)}")