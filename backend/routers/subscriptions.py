"""
Subscriptions router
The Scribe's Service Tiers
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import List

from database.connection import get_database
from models.user import User, SubscriptionTier
from routers.auth import get_current_user
from services.payment_service import PaymentService

router = APIRouter()

class SubscriptionTierResponse(BaseModel):
    id: int
    name: str
    price_usd: float
    context_limit: int
    description: str

class PaymentInitiation(BaseModel):
    tier_id: int

@router.get("/tiers", response_model=List[SubscriptionTierResponse])
async def get_subscription_tiers(
    db: AsyncSession = Depends(get_database)
):
    """
    Get available subscription tiers
    The Scribe's Service Offerings
    """
    try:
        result = await db.execute(
            select(SubscriptionTier).order_by(SubscriptionTier.price_usd)
        )
        tiers = result.scalars().all()
        
        return [
            SubscriptionTierResponse(
                id=tier.id,
                name=tier.name,
                price_usd=float(tier.price_usd),
                context_limit=tier.context_limit,
                description=tier.description
            )
            for tier in tiers
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get subscription tiers")

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
        # Get tier information
        tier_result = await db.execute(
            select(SubscriptionTier).where(SubscriptionTier.id == payment_data.tier_id)
        )
        tier = tier_result.scalar_one_or_none()
        
        if not tier:
            raise HTTPException(status_code=404, detail="Subscription tier not found")
        
        # Initiate payment
        payment_service = PaymentService()
        result = await payment_service.initiate_payment(
            user_id=current_user.id,
            tier_id=tier.id,
            amount=float(tier.price_usd)
        )
        
        if result["success"]:
            return {
                "payment_url": result["redirect_url"],
                "payment_id": result["payment_id"],
                "amount": result["amount"],
                "tier_name": tier.name
            }
        else:
            raise HTTPException(status_code=500, detail=result["error"])
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to initiate payment")