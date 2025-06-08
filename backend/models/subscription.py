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
    
    # Match the exact database schema
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    price_usd = Column(Float, nullable=False)
    context_limit = Column(Integer, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())
    price_uzs = Column(Integer)
    max_daily_ai_minutes = Column(Integer, default=240)
    max_daily_sms = Column(Integer, default=100)
    has_agentic_functions = Column(Boolean, default=True)
    has_agentic_constructor = Column(Boolean, default=True)
    
    # Relationships - temporarily disabled to avoid issues
    # user_subscriptions = relationship("UserSubscription", back_populates="tier")

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    tier_id = Column(Integer, ForeignKey("subscription_tiers.id"), nullable=False)
    status = Column(String(20), default="pending")  # active, cancelled, expired, suspended, pending
    started_at = Column(DateTime)
    expires_at = Column(DateTime)
    click_trans_id = Column(Integer)
    click_merchant_trans_id = Column(String(255))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships - temporarily disabled to avoid issues
    # user = relationship("User", back_populates="subscription")
    # tier = relationship("SubscriptionTier", back_populates="user_subscriptions")