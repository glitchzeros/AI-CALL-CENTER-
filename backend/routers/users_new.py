"""
Users router
The Scribe's Client Management
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from pydantic import BaseModel
from typing import Optional
import logging

from database.connection import get_database
from models.user import User
from models.subscription import UserSubscription, SubscriptionTier
from routers.auth import get_current_user

logger = logging.getLogger(__name__)
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
        # For now, return basic profile without subscription data
        return UserProfile(
            id=current_user.id,
            email=current_user.email,
            phone_number=current_user.phone_number,
            company_number=current_user.company_number,
            is_verified=current_user.is_verified,
            created_at=current_user.created_at.isoformat(),
            current_subscription=None
        )
        
    except Exception as e:
        logger.error(f"Profile error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get user profile: {str(e)}")

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

@router.get("/test-simple")
async def test_simple():
    """
    Simple test endpoint without database
    """
    return {"status": "success", "message": "Simple test works"}

@router.get("/test-db")
async def test_database_connection(db: AsyncSession = Depends(get_database)):
    """
    Test database connection without authentication
    """
    try:
        result = await db.execute(text("SELECT 1 as test"))
        row = result.fetchone()
        return {"status": "success", "test_value": row[0]}
    except Exception as e:
        logger.error(f"Database test error: {e}")
        raise HTTPException(status_code=500, detail=f"Database test failed: {str(e)}")