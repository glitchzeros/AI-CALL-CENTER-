"""
Statistics and analytics models
The Scribe's Performance Metrics
"""

from sqlalchemy import Column, Integer, Date, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base

class CallStatistics(Base):
    __tablename__ = "call_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    total_calls = Column(Integer, default=0)
    total_duration_seconds = Column(Integer, default=0)
    positive_interactions = Column(Integer, default=0)
    negative_interactions = Column(Integer, default=0)
    total_sms_sent = Column(Integer, default=0)
    total_sms_received = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Unique constraint to prevent duplicate entries per user per day
    __table_args__ = (UniqueConstraint('user_id', 'date', name='_user_date_uc'),)
    
    # Relationships - temporarily disabled to avoid issues
    # user = relationship("User", back_populates="statistics")