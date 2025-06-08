"""
Subscriptions router
The Scribe's Service Tiers
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel
from typing import List, Optional

from database.connection import get_database
from models.user import User
from models.subscription import SubscriptionTier, UserSubscription
from routers.auth import get_current_user
from services.manual_payment_service import ManualPaymentService
from services.payment_monitoring_service import PaymentMonitoringService
from services.usage_tracking_service import UsageTrackingService
from datetime import date

router = APIRouter()

class SubscriptionTierResponse(BaseModel):
    id: int
    name: str
    display_name: Optional[str] = None
    description: Optional[str]
    price_usd: float
    price_uzs: Optional[int]
    max_daily_ai_minutes: Optional[int]
    max_daily_sms: Optional[int]
    context_limit: Optional[int]
    has_agentic_functions: Optional[bool]
    has_agentic_constructor: Optional[bool]
    features: List[str] = []

class PaymentInitiation(BaseModel):
    tier_id: int

class PaymentMonitoringRequest(BaseModel):
    tier_id: int
    bank_card_number: str

@router.get("/tiers", response_model=List[SubscriptionTierResponse])
async def get_subscription_tiers(db: AsyncSession = Depends(get_database)):
    """
    Get available subscription tiers
    The Scribe's Service Offerings
    """
    try:
        result = await db.execute(select(SubscriptionTier).order_by(SubscriptionTier.price_usd))
        tiers = result.scalars().all()
        
        return [
            SubscriptionTierResponse(
                id=tier.id,
                name=tier.name,
                display_name=tier.display_name or tier.name.replace('_', ' ').title(),
                description=tier.description or "",
                price_usd=float(tier.price_usd or 0),
                price_uzs=tier.price_uzs,
                max_daily_ai_minutes=tier.max_daily_ai_minutes,
                max_daily_sms=tier.max_daily_sms,
                context_limit=tier.context_limit,
                has_agentic_functions=tier.has_agentic_functions,
                has_agentic_constructor=tier.has_agentic_constructor
            ) for tier in tiers
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get subscription tiers: {str(e)}")

@router.post("/initiate-payment")
async def initiate_payment(
    payment_data: PaymentInitiation,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Initiate payment for subscription tier
    The Scribe's Financial Gateway
    """
    try:
        tier_result = await db.execute(
            select(SubscriptionTier).where(SubscriptionTier.id == payment_data.tier_id)
        )
        tier = tier_result.scalar_one_or_none()
        
        if not tier:
            raise HTTPException(status_code=404, detail="Subscription tier not found")
        
        payment_service = ManualPaymentService()
        result = await payment_service.initiate_consultation_payment(
            user_id=current_user.id,
            tier_name=tier.name,
            tier_price_usd=float(tier.price_usd),
            company_number=current_user.company_number
        )
        
        if result["success"]:
            return {
                "success": True,
                "payment_id": result["payment_id"],
                "reference_code": result["reference_code"],
                "amount_uzs": result["amount_uzs"],
                "expires_at": result["expires_at"],
                "payment_instructions": result["payment_instructions"],
                "bank_details": result["bank_details"],
                "tier_name": tier.name
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to initiate payment")

@router.get("/usage-status")
async def get_usage_status(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Get current user's daily usage status
    The Scribe's Usage Tracker
    """
    try:
        usage_service = UsageTrackingService()
        usage_data = await usage_service.get_user_daily_usage(
            user_id=current_user.id,
            usage_date=date.today(),
            db=db
        )
        
        return {
            "success": True,
            "usage_data": usage_data,
            "date": date.today().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get usage status")

@router.get("/my-subscription")
async def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Get current user's subscription details
    The Scribe's Membership Status
    """
    try:
        result = await db.execute(
            select(UserSubscription, SubscriptionTier)
            .join(SubscriptionTier)
            .where(
                and_(
                    UserSubscription.user_id == current_user.id,
                    UserSubscription.status == 'active'
                )
            )
        )
        subscription_data = result.first()
        
        if not subscription_data:
            return {
                "has_subscription": False,
                "subscription": None,
                "tier": None
            }
        
        subscription, tier = subscription_data
        
        usage_service = UsageTrackingService()
        usage_data = await usage_service.get_user_daily_usage(
            user_id=current_user.id,
            usage_date=date.today(),
            db=db
        )
        
        return {
            "has_subscription": True,
            "subscription": {
                "id": subscription.id,
                "status": subscription.status,
                "started_at": subscription.started_at.isoformat() if subscription.started_at else None,
                "expires_at": subscription.expires_at.isoformat() if subscription.expires_at else None,
                "auto_renew": subscription.auto_renew
            },
            "tier": {
                "id": tier.id,
                "name": tier.name,
                "display_name": tier.display_name,
                "description": tier.description,
                "price_uzs": tier.price_uzs,
                "max_daily_ai_minutes": tier.max_daily_ai_minutes,
                "max_daily_sms": tier.max_daily_sms,
                "has_agentic_functions": tier.has_agentic_functions,
                "has_agentic_constructor": tier.has_agentic_constructor
            },
            "usage": usage_data
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get subscription details: {e}")
