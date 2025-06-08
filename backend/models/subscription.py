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
    name = Column(String(50), unique=True, nullable=False)  # tier1, tier2, tier3
    display_name = Column(String(100), nullable=False)
    description = Column(Text)
    price_monthly = Column(Float, default=0.0)  # Legacy USD pricing
    price_yearly = Column(Float, default=0.0)   # Legacy USD pricing
    price_usd = Column(Float, default=0.0)      # USD pricing for compatibility
    price_uzs = Column(Integer, default=0)      # UZS pricing (main pricing)
    max_sessions_per_month = Column(Integer, default=10)  # Legacy field
    max_session_duration_minutes = Column(Integer, default=30)  # Legacy field
    max_daily_ai_minutes = Column(Integer, default=240)  # Daily AI call processing limit in minutes
    max_daily_sms = Column(Integer, default=100)  # Daily SMS limit (incoming + outgoing)
    context_limit = Column(Integer, default=1000)  # Context limit for AI processing
    has_agentic_functions = Column(Boolean, default=False)  # Access to agentic functions
    has_agentic_constructor = Column(Boolean, default=False)  # Access to agentic functions constructor
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
    payments = relationship("PaymentTransaction", back_populates="subscription")