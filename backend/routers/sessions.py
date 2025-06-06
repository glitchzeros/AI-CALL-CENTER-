"""
Sessions router
The Scribe's Conversation Management
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta

from database.connection import get_database
from models.user import User
from models.session import CommunicationSession, SessionMessage
from routers.auth import get_current_user

router = APIRouter()

class SessionResponse(BaseModel):
    id: int
    session_type: str
    caller_id: Optional[str]
    company_number: Optional[str]
    status: str
    started_at: str
    ended_at: Optional[str]
    duration_seconds: Optional[int]
    outcome: Optional[str]
    ai_summary: Optional[str]

class SessionMessageResponse(BaseModel):
    id: int
    speaker: str
    message_type: str
    content: Optional[str]
    timestamp: str
    metadata: Optional[dict]

class SessionDetailResponse(BaseModel):
    session: SessionResponse
    messages: List[SessionMessageResponse]

@router.get("/", response_model=List[SessionResponse])
async def get_user_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database),
    limit: int = 50,
    offset: int = 0,
    session_type: Optional[str] = None,
    status: Optional[str] = None
):
    """
    Get user's communication sessions
    The Scribe's Conversation History
    """
    try:
        query = select(CommunicationSession).where(
            CommunicationSession.user_id == current_user.id
        )
        
        if session_type:
            query = query.where(CommunicationSession.session_type == session_type)
        
        if status:
            query = query.where(CommunicationSession.status == status)
        
        query = query.order_by(desc(CommunicationSession.started_at)).limit(limit).offset(offset)
        
        result = await db.execute(query)
        sessions = result.scalars().all()
        
        return [
            SessionResponse(
                id=session.id,
                session_type=session.session_type,
                caller_id=session.caller_id,
                company_number=session.company_number,
                status=session.status,
                started_at=session.started_at.isoformat(),
                ended_at=session.ended_at.isoformat() if session.ended_at else None,
                duration_seconds=session.duration_seconds,
                outcome=session.outcome,
                ai_summary=session.ai_summary
            )
            for session in sessions
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get sessions")

@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session_detail(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Get detailed session information with messages
    The Scribe's Conversation Record
    """
    try:
        # Get session
        session_result = await db.execute(
            select(CommunicationSession).where(
                CommunicationSession.id == session_id,
                CommunicationSession.user_id == current_user.id
            )
        )
        session = session_result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get messages
        messages_result = await db.execute(
            select(SessionMessage).where(
                SessionMessage.session_id == session_id
            ).order_by(SessionMessage.timestamp)
        )
        messages = messages_result.scalars().all()
        
        return SessionDetailResponse(
            session=SessionResponse(
                id=session.id,
                session_type=session.session_type,
                caller_id=session.caller_id,
                company_number=session.company_number,
                status=session.status,
                started_at=session.started_at.isoformat(),
                ended_at=session.ended_at.isoformat() if session.ended_at else None,
                duration_seconds=session.duration_seconds,
                outcome=session.outcome,
                ai_summary=session.ai_summary
            ),
            messages=[
                SessionMessageResponse(
                    id=msg.id,
                    speaker=msg.speaker,
                    message_type=msg.message_type,
                    content=msg.content,
                    timestamp=msg.timestamp.isoformat(),
                    metadata=msg.metadata
                )
                for msg in messages
            ]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get session detail")

@router.get("/active/count")
async def get_active_sessions_count(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Get count of active sessions
    The Scribe's Current Activity
    """
    try:
        result = await db.execute(
            select(CommunicationSession).where(
                CommunicationSession.user_id == current_user.id,
                CommunicationSession.status == "active"
            )
        )
        active_sessions = result.scalars().all()
        
        return {
            "active_count": len(active_sessions),
            "sessions": [
                {
                    "id": session.id,
                    "type": session.session_type,
                    "caller_id": session.caller_id,
                    "started_at": session.started_at.isoformat()
                }
                for session in active_sessions
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get active sessions")

@router.get("/recent/summary")
async def get_recent_sessions_summary(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database),
    hours: int = 24
):
    """
    Get summary of recent sessions
    The Scribe's Recent Activity
    """
    try:
        since = datetime.utcnow() - timedelta(hours=hours)
        
        result = await db.execute(
            select(CommunicationSession).where(
                CommunicationSession.user_id == current_user.id,
                CommunicationSession.started_at >= since
            )
        )
        sessions = result.scalars().all()
        
        # Calculate summary statistics
        total_sessions = len(sessions)
        completed_sessions = len([s for s in sessions if s.status == "completed"])
        positive_outcomes = len([s for s in sessions if s.outcome == "positive"])
        negative_outcomes = len([s for s in sessions if s.outcome == "negative"])
        
        total_duration = sum([s.duration_seconds or 0 for s in sessions])
        
        # Group by session type
        by_type = {}
        for session in sessions:
            session_type = session.session_type
            if session_type not in by_type:
                by_type[session_type] = 0
            by_type[session_type] += 1
        
        return {
            "period_hours": hours,
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "positive_outcomes": positive_outcomes,
            "negative_outcomes": negative_outcomes,
            "total_duration_seconds": total_duration,
            "average_duration_seconds": total_duration // total_sessions if total_sessions > 0 else 0,
            "sessions_by_type": by_type,
            "success_rate": (positive_outcomes / completed_sessions * 100) if completed_sessions > 0 else 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get sessions summary")