"""
GSM Module models
The Scribe's Communication Device Registry
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base

class GSMModule(Base):
    __tablename__ = "gsm_modules"
    
    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(20), unique=True, nullable=False, index=True)
    bank_card_number = Column(String(20), unique=True, nullable=False, index=True)
    bank_name = Column(String(100), nullable=False)
    card_holder_name = Column(String(100), nullable=False)
    device_id = Column(String(50), unique=True, nullable=True)  # SIM800C device identifier
    is_active = Column(Boolean, default=True)
    is_available = Column(Boolean, default=True)  # Available for sending SMS
    last_used_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Configuration
    description = Column(Text)
    priority = Column(Integer, default=1)  # Higher number = higher priority
    
    # Status tracking
    status = Column(String(20), default="idle")  # idle, busy, error, offline
    last_error = Column(Text)
    error_count = Column(Integer, default=0)
    
    # Relationships
    payment_sessions = relationship("PaymentSession", back_populates="gsm_module")

class PaymentSession(Base):
    __tablename__ = "payment_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    gsm_module_id = Column(Integer, ForeignKey("gsm_modules.id"), nullable=False)
    subscription_tier = Column(String(50), nullable=False)
    amount_uzs = Column(Integer, nullable=False)  # Amount in UZS
    amount_usd = Column(Integer, nullable=False)  # Amount in USD cents
    
    # Payment instructions
    bank_card_number = Column(String(20), nullable=False)
    bank_name = Column(String(100), nullable=False)
    card_holder_name = Column(String(100), nullable=False)
    
    # Session timing
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)  # 30 minutes from creation
    confirmed_at = Column(DateTime)
    
    # Status
    status = Column(String(20), default="pending")  # pending, confirmed, expired, cancelled
    confirmation_sms = Column(Text)  # The SMS that confirmed payment
    confirmation_amount = Column(Integer)  # Amount found in confirmation SMS
    
    # Relationships
    user = relationship("User")
    gsm_module = relationship("GSMModule", back_populates="payment_sessions")

