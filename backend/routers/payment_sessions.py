"""
Payment Sessions Router
The Scribe's Payment Monitoring System
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
from typing import List, Optional
import logging
from datetime import datetime, timedelta

from database.connection import get_database
from models.gsm_module import PaymentSession, GSMModule
from models.user import User
from services.gsm_service import GSMService
from routers.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models
class PaymentSessionCreate(BaseModel):
    tier_name: str

class PaymentSessionResponse(BaseModel):
    id: int
    subscription_tier: str
    amount_uzs: int
    amount_usd: int
    bank_card_number: str
    bank_name: str
    card_holder_name: str
    status: str
    created_at: str
    expires_at: str
    confirmed_at: Optional[str]
    time_remaining_seconds: int

class SMSConfirmationRequest(BaseModel):
    sms_content: str
    sender_number: str
    company_number: str

@router.post("/initiate", response_model=PaymentSessionResponse)
async def initiate_payment_session(
    payment_data: PaymentSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Initiate payment session for subscription
    """
    try:
        # Define tier pricing (in USD cents)
        tier_pricing = {
            "Apprentice": 500,  # $5.00
            "Journeyman": 1500,  # $15.00
            "Master Scribe": 3000  # $30.00
        }
        
        amount_usd = tier_pricing.get(payment_data.tier_name)
        if not amount_usd:
            raise HTTPException(status_code=400, detail="Invalid subscription tier")
        
        gsm_service = GSMService()
        session = await gsm_service.create_payment_session(
            db=db,
            user_id=current_user.id,
            subscription_tier=payment_data.tier_name,
            amount_usd=amount_usd
        )
        
        # Calculate time remaining
        now = datetime.utcnow()
        time_remaining = max(0, int((session.expires_at - now).total_seconds()))
        
        logger.info(f"Payment session {session.id} initiated for user {current_user.id}")
        
        return PaymentSessionResponse(
            id=session.id,
            subscription_tier=session.subscription_tier,
            amount_uzs=session.amount_uzs,
            amount_usd=session.amount_usd,
            bank_card_number=session.bank_card_number,
            bank_name=session.bank_name,
            card_holder_name=session.card_holder_name,
            status=session.status,
            created_at=session.created_at.isoformat(),
            expires_at=session.expires_at.isoformat(),
            confirmed_at=session.confirmed_at.isoformat() if session.confirmed_at else None,
            time_remaining_seconds=time_remaining
        )
        
    except Exception as e:
        logger.error(f"Error initiating payment session: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate payment session")

@router.get("/active", response_model=Optional[PaymentSessionResponse])
async def get_active_payment_session(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Get active payment session for current user
    """
    try:
        result = await db.execute(
            select(PaymentSession)
            .where(
                and_(
                    PaymentSession.user_id == current_user.id,
                    PaymentSession.status == "pending",
                    PaymentSession.expires_at > datetime.utcnow()
                )
            )
            .order_by(PaymentSession.created_at.desc())
            .limit(1)
        )
        session = result.scalar_one_or_none()
        
        if not session:
            return None
        
        # Calculate time remaining
        now = datetime.utcnow()
        time_remaining = max(0, int((session.expires_at - now).total_seconds()))
        
        return PaymentSessionResponse(
            id=session.id,
            subscription_tier=session.subscription_tier,
            amount_uzs=session.amount_uzs,
            amount_usd=session.amount_usd,
            bank_card_number=session.bank_card_number,
            bank_name=session.bank_name,
            card_holder_name=session.card_holder_name,
            status=session.status,
            created_at=session.created_at.isoformat(),
            expires_at=session.expires_at.isoformat(),
            confirmed_at=session.confirmed_at.isoformat() if session.confirmed_at else None,
            time_remaining_seconds=time_remaining
        )
        
    except Exception as e:
        logger.error(f"Error getting active payment session: {e}")
        raise HTTPException(status_code=500, detail="Failed to get payment session")

@router.post("/confirm-sms")
async def confirm_payment_sms(
    sms_data: SMSConfirmationRequest,
    db: AsyncSession = Depends(get_database)
):
    """
    Confirm payment via SMS analysis
    Called by modem manager when SMS is received
    """
    try:
        gsm_service = GSMService()
        result = await gsm_service.check_payment_confirmation(
            db=db,
            sms_content=sms_data.sms_content,
            sender_number=sms_data.sender_number,
            company_number=sms_data.company_number
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error confirming payment SMS: {e}")
        raise HTTPException(status_code=500, detail="Failed to process SMS confirmation")

@router.get("/history", response_model=List[PaymentSessionResponse])
async def get_payment_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database),
    limit: int = 10
):
    """
    Get payment history for current user
    """
    try:
        result = await db.execute(
            select(PaymentSession)
            .where(PaymentSession.user_id == current_user.id)
            .order_by(PaymentSession.created_at.desc())
            .limit(limit)
        )
        sessions = result.scalars().all()
        
        payment_history = []
        for session in sessions:
            # Calculate time remaining (0 if expired)
            now = datetime.utcnow()
            time_remaining = max(0, int((session.expires_at - now).total_seconds()))
            
            payment_history.append(PaymentSessionResponse(
                id=session.id,
                subscription_tier=session.subscription_tier,
                amount_uzs=session.amount_uzs,
                amount_usd=session.amount_usd,
                bank_card_number=session.bank_card_number,
                bank_name=session.bank_name,
                card_holder_name=session.card_holder_name,
                status=session.status,
                created_at=session.created_at.isoformat(),
                expires_at=session.expires_at.isoformat(),
                confirmed_at=session.confirmed_at.isoformat() if session.confirmed_at else None,
                time_remaining_seconds=time_remaining
            ))
        
        return payment_history
        
    except Exception as e:
        logger.error(f"Error getting payment history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get payment history")

@router.post("/{session_id}/cancel")
async def cancel_payment_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Cancel active payment session
    """
    try:
        result = await db.execute(
            select(PaymentSession)
            .where(
                and_(
                    PaymentSession.id == session_id,
                    PaymentSession.user_id == current_user.id,
                    PaymentSession.status == "pending"
                )
            )
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Payment session not found")
        
        session.status = "cancelled"
        await db.commit()
        
        logger.info(f"Payment session {session_id} cancelled by user {current_user.id}")
        
        return {"message": "Payment session cancelled successfully"}
        
    except Exception as e:
        logger.error(f"Error cancelling payment session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel payment session")

@router.get("/{session_id}/status", response_model=PaymentSessionResponse)
async def get_payment_session_status(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Get status of specific payment session
    """
    try:
        result = await db.execute(
            select(PaymentSession)
            .where(
                and_(
                    PaymentSession.id == session_id,
                    PaymentSession.user_id == current_user.id
                )
            )
        )
        session = result.scalar_one_or_none()
        
        if not session:
            raise HTTPException(status_code=404, detail="Payment session not found")
        
        # Calculate time remaining
        now = datetime.utcnow()
        time_remaining = max(0, int((session.expires_at - now).total_seconds()))
        
        return PaymentSessionResponse(
            id=session.id,
            subscription_tier=session.subscription_tier,
            amount_uzs=session.amount_uzs,
            amount_usd=session.amount_usd,
            bank_card_number=session.bank_card_number,
            bank_name=session.bank_name,
            card_holder_name=session.card_holder_name,
            status=session.status,
            created_at=session.created_at.isoformat(),
            expires_at=session.expires_at.isoformat(),
            confirmed_at=session.confirmed_at.isoformat() if session.confirmed_at else None,
            time_remaining_seconds=time_remaining
        )
        
    except Exception as e:
        logger.error(f"Error getting payment session status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get payment session status")