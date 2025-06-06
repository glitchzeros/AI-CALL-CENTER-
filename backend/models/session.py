"""
Communication session models
The Scribe's Conversation Records
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base

class CommunicationSession(Base):
    __tablename__ = "communication_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_type = Column(String(20), nullable=False)  # voice, sms, telegram
    caller_id = Column(String(50))  # Phone number or Telegram handle
    company_number = Column(String(20))  # The assigned company number
    status = Column(String(20), default="active")  # active, completed, failed, abandoned
    started_at = Column(DateTime, default=func.now())
    ended_at = Column(DateTime)
    duration_seconds = Column(Integer)
    outcome = Column(String(20))  # positive, negative, neutral
    ai_summary = Column(Text)
    context_data = Column(JSON)  # Conversation history and context
    current_invocation_state = Column(JSON)  # Current workflow state
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")
    messages = relationship("SessionMessage", back_populates="session")

class SessionMessage(Base):
    __tablename__ = "session_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("communication_sessions.id"), nullable=False)
    speaker = Column(String(10), nullable=False)  # user, ai
    message_type = Column(String(20), nullable=False)  # text, audio, sms
    content = Column(Text)
    audio_file_path = Column(String(500))
    timestamp = Column(DateTime, default=func.now())
    metadata = Column(JSON)  # Additional data like audio features, language detected, etc.
    
    # Relationships
    session = relationship("CommunicationSession", back_populates="messages")