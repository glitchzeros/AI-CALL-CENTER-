"""
Subscription models
The Scribe's Membership Records
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.connection import Base

class SubscriptionTier(Base):
    __tablename__ = "subscription_tiers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)  # free, basic, premium, enterprise
    display_name = Column(String(100), nullable=False)
    description = Column(Text)
    price_monthly = Column(Float, default=0.0)
    price_yearly = Column(Float, default=0.0)
    max_sessions_per_month = Column(Integer, default=10)
    max_session_duration_minutes = Column(Integer, default=30)
    features = Column(Text)  # JSON string of features
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user_subscriptions = relationship("UserSubscription", back_populates="tier")

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tier_id = Column(Integer, ForeignKey("subscription_tiers.id"), nullable=False)
    status = Column(String(20), default="active")  # active, cancelled, expired, suspended
    started_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime)
    auto_renew = Column(Boolean, default=True)
    payment_method = Column(String(50))  # card, bank_transfer, crypto, etc.
    last_payment_date = Column(DateTime)
    next_payment_date = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="subscription")
    tier = relationship("SubscriptionTier", back_populates="user_subscriptions")