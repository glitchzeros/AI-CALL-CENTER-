"""
User models
The Scribe's Client Registry
"""

from __future__ import annotations
from typing import List, TYPE_CHECKING
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
from database.connection import Base

if TYPE_CHECKING:
    from .subscription import UserSubscription
    from .workflow import ScribeWorkflow
    from .session import CommunicationSession
    from .statistics import CallStatistics
    from .payment import PaymentTransaction, ManualPaymentSession
    from .sms_verification import SMSVerificationSession
    from .company_number import CompanyNumberPool

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=True)
    company_number: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # SMS verification for registration
    sms_verification_code: Mapped[str] = mapped_column(String(6), nullable=True)
    sms_verification_expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    subscription: Mapped["UserSubscription"] = relationship(back_populates="user", uselist=False)
    workflows: Mapped[List["ScribeWorkflow"]] = relationship(back_populates="user")
    sessions: Mapped[List["CommunicationSession"]] = relationship(back_populates="user")
    statistics: Mapped[List["CallStatistics"]] = relationship(back_populates="user")
    payments: Mapped[List["PaymentTransaction"]] = relationship(back_populates="user")
    manual_payments: Mapped[List["ManualPaymentSession"]] = relationship(back_populates="user")
    sms_verification_sessions: Mapped[List["SMSVerificationSession"]] = relationship(back_populates="user")
    assigned_company_number: Mapped["CompanyNumberPool"] = relationship(back_populates="assigned_user")
