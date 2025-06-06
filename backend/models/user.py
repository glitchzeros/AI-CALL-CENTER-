"""
User and subscription models
The Scribe's Client Registry
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, DECIMAL, Text
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
    sms_verification_code = Column(String(6))
    sms_verification_expires_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    subscriptions = relationship("UserSubscription", back_populates="user")
    workflows = relationship("ScribeWorkflow", back_populates="user")
    sessions = relationship("CommunicationSession", back_populates="user")
    statistics = relationship("CallStatistics", back_populates="user")
    payments = relationship("PaymentTransaction", back_populates="user")

class SubscriptionTier(Base):
    __tablename__ = "subscription_tiers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    price_usd = Column(DECIMAL(10, 2), nullable=False)
    context_limit = Column(Integer, nullable=False)  # -1 for unlimited
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    subscriptions = relationship("UserSubscription", back_populates="tier")

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tier_id = Column(Integer, ForeignKey("subscription_tiers.id"), nullable=False)
    status = Column(String(20), default="pending")  # pending, active, expired, cancelled
    started_at = Column(DateTime)
    expires_at = Column(DateTime)
    click_trans_id = Column(Integer)
    click_merchant_trans_id = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")
    tier = relationship("SubscriptionTier", back_populates="subscriptions")
    payments = relationship("PaymentTransaction", back_populates="subscription")