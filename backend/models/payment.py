"""
Payment transaction models
The Scribe's Financial Records
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL, Text, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subscription_id = Column(Integer, ForeignKey("user_subscriptions.id"))
    click_trans_id = Column(BigInteger, unique=True)
    click_paydoc_id = Column(BigInteger)
    merchant_trans_id = Column(String(255))
    merchant_prepare_id = Column(Integer)
    amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(String(20), default="pending")  # pending, completed, failed, cancelled
    error_code = Column(Integer)
    error_note = Column(Text)
    sign_time = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="payments")
    subscription = relationship("UserSubscription", back_populates="payments")

class ManualPaymentSession(Base):
    __tablename__ = "manual_payment_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    payment_id = Column(String(100), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tier_name = Column(String(50), nullable=False)
    amount_usd = Column(DECIMAL(10, 2), nullable=False)
    amount_uzs = Column(DECIMAL(12, 0), nullable=False)
    reference_code = Column(String(20), unique=True, nullable=False)
    company_number = Column(String(20), nullable=False)
    status = Column(String(20), default="pending")  # pending, confirmed, expired, cancelled
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)
    confirmed_at = Column(DateTime, nullable=True)
    sms_content = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User")