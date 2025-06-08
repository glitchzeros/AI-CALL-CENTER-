"""
User models
The Scribe's Client Registry
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    company_number = Column(String(20), unique=True, index=True)
    is_verified = Column(Boolean, default=False)
    
    # SMS verification for registration
    sms_verification_code = Column(String(6))
    sms_verification_expires_at = Column(DateTime)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    subscription = relationship("UserSubscription", back_populates="user", uselist=False)
    workflows = relationship("ScribeWorkflow", back_populates="user")
    sessions = relationship("CommunicationSession", back_populates="user")
    statistics = relationship("CallStatistics", back_populates="user")
    payments = relationship("PaymentTransaction", back_populates="user")
    sms_verification_sessions = relationship("SMSVerificationSession", back_populates="user")