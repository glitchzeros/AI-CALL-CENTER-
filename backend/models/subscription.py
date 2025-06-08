"""
Subscription models
The Scribe's Membership Records
"""
from __future__ import annotations
from typing import List, TYPE_CHECKING
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Text
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from database.connection import Base

if TYPE_CHECKING:
    from .user import User

class SubscriptionTier(Base):
    __tablename__ = "subscription_tiers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    price_usd: Mapped[float] = mapped_column(Float, nullable=False)
    price_uzs: Mapped[int] = mapped_column(Integer, nullable=True)
    context_limit: Mapped[int] = mapped_column(Integer, nullable=False)
    max_daily_ai_minutes: Mapped[int] = mapped_column(Integer, default=240)
    max_daily_sms: Mapped[int] = mapped_column(Integer, default=100)
    has_agentic_functions: Mapped[bool] = mapped_column(Boolean, default=True)
    has_agentic_constructor: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    user_subscriptions: Mapped[List["UserSubscription"]] = relationship(back_populates="tier")

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    tier_id: Mapped[int] = mapped_column(Integer, ForeignKey("subscription_tiers.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    user: Mapped["User"] = relationship(back_populates="subscription")
    tier: Mapped["SubscriptionTier"] = relationship(back_populates="user_subscriptions")
