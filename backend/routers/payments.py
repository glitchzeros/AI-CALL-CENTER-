"""
Manual Payments router
The Scribe's Bank Transfer Interface
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

from database.connection import get_database
from models.user import User
from models.subscription import SubscriptionTier, UserSubscription
from routers.auth import get_current_user
from services.manual_payment_service import ManualPaymentService

logger = logging.getLogger("aetherium.manual_payments")

router = APIRouter()
payment_service = ManualPaymentService()

class PaymentInitiationRequest(BaseModel):
    tier_name: str

class PaymentSessionResponse(BaseModel):
    payment_id: str
    tier_name: str
    amount_uzs: float
    amount_usd: float
    reference_code: str
    status: str
    created_at: str
    expires_at: str
    confirmed_at: Optional[str] = None

class SMSConfirmationRequest(BaseModel):
    sms_content: str
    sender_number: Optional[str] = None
    company_number: Optional[str] = None

@router.post("/initiate-consultation")
async def initiate_consultation_payment(
    payment_data: PaymentInitiationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Initiate payment after AI consultation
    The Scribe's Payment Awakening
    """
    try:
        # Get tier information
        result = await db.execute(
            select(SubscriptionTier).where(SubscriptionTier.name == payment_data.tier_name)
        )
        tier = result.scalar_one_or_none()
        
        if not tier:
            raise HTTPException(status_code=404, detail="Subscription tier not found")
        
        # Check if user already has active payment session
        existing_session = payment_service.get_session_by_user(current_user.id)
        if existing_session:
            await payment_service.cancel_payment_session(existing_session.payment_id)
        
        # Initiate payment
        result = await payment_service.initiate_consultation_payment(
            user_id=current_user.id,
            tier_name=payment_data.tier_name,
            tier_price_usd=float(tier.price_usd),
            company_number=current_user.company_number
        )
        
        if result["success"]:
            # Store session in database
            from models.payment import ManualPaymentSession
            
            session = ManualPaymentSession(
                payment_id=result["payment_id"],
                user_id=current_user.id,
                tier_name=payment_data.tier_name,
                amount_usd=float(tier.price_usd),
                amount_uzs=result["amount_uzs"],
                reference_code=result["reference_code"],
                company_number=current_user.company_number,
                expires_at=datetime.fromisoformat(result["expires_at"].replace('Z', '+00:00'))
            )
            
            db.add(session)
            await db.commit()
            
            return {
                "success": True,
                "payment_id": result["payment_id"],
                "reference_code": result["reference_code"],
                "amount_uzs": result["amount_uzs"],
                "amount_usd": result["amount_usd"],
                "expires_at": result["expires_at"],
                "remaining_minutes": result["remaining_minutes"],
                "payment_instructions": result["payment_instructions"],
                "bank_details": result["bank_details"]
            }
        else:
            raise HTTPException(status_code=400, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initiating consultation payment: {e}")
        raise HTTPException(status_code=500, detail="Payment initiation failed")

@router.get("/status/{payment_id}")
async def get_payment_status(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Get payment session status
    The Scribe's Payment Inquiry
    """
    try:
        result = await payment_service.check_payment_status(payment_id)
        
        if result["success"]:
            return {
                "success": True,
                "payment_id": payment_id,
                "status": result["status"],
                "remaining_minutes": result["remaining_minutes"],
                "is_expired": result["is_expired"]
            }
        else:
            raise HTTPException(status_code=404, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get payment status")

@router.post("/confirm-sms")
async def confirm_sms_payment(
    sms_data: SMSConfirmationRequest,
    db: AsyncSession = Depends(get_database)
):
    """
    Process SMS confirmation for payment
    The Scribe's Financial Confirmation
    """
    try:
        result = await payment_service.process_sms_confirmation(
            sms_content=sms_data.sms_content,
            company_number=sms_data.company_number or "",
            sender_number=sms_data.sender_number or "unknown"
        )
        
        if result["success"] and result["confirmed"]:
            # Update database session
            from models.payment import ManualPaymentSession
            
            await db.execute(
                update(ManualPaymentSession)
                .where(ManualPaymentSession.payment_id == result["payment_id"])
                .values(
                    status="confirmed",
                    confirmed_at=datetime.utcnow(),
                    sms_content=sms_data.sms_content
                )
            )
            
            # Activate user subscription
            await _activate_user_subscription(
                db, result["user_id"], result["tier_name"]
            )
            
            await db.commit()
            
            logger.info(f"Payment confirmed via SMS for user {result['user_id']}")
            
            return {
                "success": True,
                "confirmed": True,
                "user_id": result["user_id"],
                "tier_name": result["tier_name"]
            }
        else:
            return {
                "success": True,
                "confirmed": False,
                "reason": result.get("reason", "SMS not recognized as payment")
            }
            
    except Exception as e:
        logger.error(f"Error confirming SMS payment: {e}")
        raise HTTPException(status_code=500, detail="SMS confirmation failed")

@router.post("/cancel/{payment_id}")
async def cancel_payment(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Cancel payment session
    The Scribe's Payment Cancellation
    """
    try:
        success = await payment_service.cancel_payment_session(payment_id)
        
        if success:
            # Update database
            from models.payment import ManualPaymentSession
            
            await db.execute(
                update(ManualPaymentSession)
                .where(ManualPaymentSession.payment_id == payment_id)
                .where(ManualPaymentSession.user_id == current_user.id)
                .values(status="cancelled")
            )
            await db.commit()
            
            return {"success": True, "message": "Payment session cancelled"}
        else:
            raise HTTPException(status_code=404, detail="Payment session not found or already processed")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling payment: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel payment")

@router.get("/bank-info")
async def get_bank_info():
    """
    Get company bank information
    The Scribe's Financial Details
    """
    try:
        bank_info = payment_service.get_company_bank_info()
        return {
            "success": True,
            "bank_info": bank_info
        }
    except Exception as e:
        logger.error(f"Error getting bank info: {e}")
        raise HTTPException(status_code=500, detail="Failed to get bank information")

@router.get("/sessions", response_model=List[PaymentSessionResponse])
async def get_payment_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Get user's payment sessions
    The Scribe's Payment History
    """
    try:
        from models.payment import ManualPaymentSession
        
        result = await db.execute(
            select(ManualPaymentSession)
            .where(ManualPaymentSession.user_id == current_user.id)
            .order_by(desc(ManualPaymentSession.created_at))
            .limit(10)
        )
        sessions = result.scalars().all()
        
        return [
            PaymentSessionResponse(
                payment_id=session.payment_id,
                tier_name=session.tier_name,
                amount_uzs=float(session.amount_uzs),
                amount_usd=float(session.amount_usd),
                reference_code=session.reference_code,
                status=session.status,
                created_at=session.created_at.isoformat(),
                expires_at=session.expires_at.isoformat(),
                confirmed_at=session.confirmed_at.isoformat() if session.confirmed_at else None
            )
            for session in sessions
        ]
        
    except Exception as e:
        logger.error(f"Error getting payment sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to get payment sessions")

async def _activate_user_subscription(db: AsyncSession, user_id: int, tier_name: str):
    """Activate user subscription after payment confirmation"""
    try:
        # Get tier
        result = await db.execute(
            select(SubscriptionTier).where(SubscriptionTier.name == tier_name)
        )
        tier = result.scalar_one_or_none()
        
        if not tier:
            logger.error(f"Tier not found: {tier_name}")
            return
        
        # Check for existing subscription
        result = await db.execute(
            select(UserSubscription).where(UserSubscription.user_id == user_id)
        )
        existing_subscription = result.scalar_one_or_none()
        
        if existing_subscription:
            # Update existing subscription
            await db.execute(
                update(UserSubscription)
                .where(UserSubscription.user_id == user_id)
                .values(
                    tier_id=tier.id,
                    is_active=True,
                    started_at=datetime.utcnow(),
                    expires_at=datetime.utcnow().replace(day=28) + timedelta(days=32)  # Next month
                )
            )
        else:
            # Create new subscription
            subscription = UserSubscription(
                user_id=user_id,
                tier_id=tier.id,
                is_active=True,
                started_at=datetime.utcnow(),
                expires_at=datetime.utcnow().replace(day=28) + timedelta(days=32)
            )
            db.add(subscription)
        
        logger.info(f"Activated subscription {tier_name} for user {user_id}")
        
    except Exception as e:
        logger.error(f"Error activating subscription: {e}")
        raise