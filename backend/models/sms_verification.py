"""
SMS Verification models
Enhanced SMS verification and monitoring
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base

class SMSVerificationSession(Base):
    __tablename__ = "sms_verification_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_type = Column(String(20), nullable=False)  # login, registration, payment
    phone_number = Column(String(20), nullable=False)
    verification_code = Column(String(6), nullable=False)
    status = Column(String(20), default="pending")  # pending, verified, expired, failed
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=3)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)
    verified_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="sms_verification_sessions")

class PaymentMonitoringSession(Base):
    __tablename__ = "payment_monitoring_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_tier_id = Column(Integer, ForeignKey("subscription_tiers.id"), nullable=False)
    company_number = Column(String(20), nullable=False)
    bank_card_number = Column(String(20), nullable=False)
    amount_usd = Column(DECIMAL(10,2), nullable=False)
    amount_uzs = Column(DECIMAL(12,0), nullable=False)
    reference_code = Column(String(20), unique=True, nullable=False)
    status = Column(String(20), default="monitoring")  # monitoring, confirmed, expired, cancelled
    started_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)
    confirmed_at = Column(DateTime)
    last_sms_check = Column(DateTime, default=func.now())
    sms_content = Column(Text)
    
    # Relationships
    user = relationship("User")
    subscription_tier = relationship("SubscriptionTier")

class GSMModuleManagement(Base):
    __tablename__ = "gsm_module_management"
    
    id = Column(Integer, primary_key=True, index=True)
    modem_id = Column(Integer, ForeignKey("gsm_modems.id"))
    action_type = Column(String(20), nullable=False)  # create, update, delete, assign, unassign
    performed_by = Column(Integer, ForeignKey("users.id"))
    action_data = Column(Text)  # JSON string of action details
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    modem = relationship("GSMModem")
    performed_by_user = relationship("User")