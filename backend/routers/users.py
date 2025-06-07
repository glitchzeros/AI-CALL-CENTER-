"""
Users router
The Scribe's Client Management
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from typing import Optional

from database.connection import get_database
from models.user import User
from models.subscription import UserSubscription, SubscriptionTier
from routers.auth import get_current_user

router = APIRouter()

class UserProfile(BaseModel):
    id: int
    email: str
    phone_number: str
    company_number: Optional[str]
    is_verified: bool
    created_at: str
    current_subscription: Optional[dict] = None

@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Get current user profile
    The Scribe's Client Record
    """
    try:
        # Get current subscription
        subscription_result = await db.execute(
            select(UserSubscription, SubscriptionTier).join(
                SubscriptionTier, UserSubscription.tier_id == SubscriptionTier.id
            ).where(
                UserSubscription.user_id == current_user.id,
                UserSubscription.status == "active"
            ).order_by(UserSubscription.created_at.desc())
        )
        
        subscription_data = subscription_result.first()
        current_subscription = None
        
        if subscription_data:
            subscription, tier = subscription_data
            current_subscription = {
                "tier_name": tier.name,
                "price_usd": float(tier.price_usd),
                "context_limit": tier.context_limit,
                "status": subscription.status,
                "started_at": subscription.started_at.isoformat() if subscription.started_at else None,
                "expires_at": subscription.expires_at.isoformat() if subscription.expires_at else None
            }
        
        return UserProfile(
            id=current_user.id,
            email=current_user.email,
            phone_number=current_user.phone_number,
            company_number=current_user.company_number,
            is_verified=current_user.is_verified,
            created_at=current_user.created_at.isoformat(),
            current_subscription=current_subscription
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get user profile")

@router.get("/company-number")
async def get_company_number(
    current_user: User = Depends(get_current_user)
):
    """
    Get user's assigned company number
    The Scribe's Direct Line
    """
    if not current_user.company_number:
        raise HTTPException(status_code=404, detail="No company number assigned")
    
    return {
        "company_number": current_user.company_number,
        "message": "This is your Scribe's direct line. It is the conduit for your automated conversations. Guard it well."
    }