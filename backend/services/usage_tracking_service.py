"""
Usage Tracking Service
Tracks and enforces daily usage limits for AI minutes and SMS
"""

from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.dialects.postgresql import insert
from typing import Dict, Optional

from models.user import User
from models.subscription import SubscriptionTier, UserSubscription


class UsageTrackingService:
    """Service for tracking and enforcing daily usage limits"""
    
    async def get_user_daily_usage(self, user_id: int, usage_date: date, db: AsyncSession) -> Dict:
        """Get user's daily usage for a specific date"""
        try:
            # First, get the user's current subscription tier
            subscription_result = await db.execute(
                select(UserSubscription, SubscriptionTier)
                .join(SubscriptionTier)
                .where(
                    and_(
                        UserSubscription.user_id == user_id,
                        UserSubscription.status == 'active'
                    )
                )
            )
            subscription_data = subscription_result.first()
            
            if not subscription_data:
                return {
                    "error": "No active subscription found",
                    "ai_minutes_used": 0,
                    "sms_count_used": 0,
                    "ai_minutes_limit": 0,
                    "sms_limit": 0,
                    "can_use_ai": False,
                    "can_send_sms": False
                }
            
            subscription, tier = subscription_data
            
            # Get daily usage from user_daily_usage table
            from models.subscription import Base
            from sqlalchemy import Column, Integer, Date, ForeignKey
            
            # Define the user_daily_usage table model inline if not already defined
            class UserDailyUsage(Base):
                __tablename__ = "user_daily_usage"
                
                id = Column(Integer, primary_key=True, index=True)
                user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
                usage_date = Column(Date, nullable=False)
                ai_minutes_used = Column(Integer, default=0)
                sms_count_used = Column(Integer, default=0)
            
            usage_result = await db.execute(
                select(UserDailyUsage).where(
                    and_(
                        UserDailyUsage.user_id == user_id,
                        UserDailyUsage.usage_date == usage_date
                    )
                )
            )
            usage_record = usage_result.scalar_one_or_none()
            
            ai_minutes_used = usage_record.ai_minutes_used if usage_record else 0
            sms_count_used = usage_record.sms_count_used if usage_record else 0
            
            # Check limits
            ai_minutes_limit = tier.max_daily_ai_minutes
            sms_limit = tier.max_daily_sms
            
            # For unlimited tiers (999999), consider as unlimited
            can_use_ai = ai_minutes_limit >= 999999 or ai_minutes_used < ai_minutes_limit
            can_send_sms = sms_limit >= 999999 or sms_count_used < sms_limit
            
            return {
                "ai_minutes_used": ai_minutes_used,
                "sms_count_used": sms_count_used,
                "ai_minutes_limit": ai_minutes_limit,
                "sms_limit": sms_limit,
                "can_use_ai": can_use_ai,
                "can_send_sms": can_send_sms,
                "tier_name": tier.name,
                "tier_display_name": tier.display_name
            }
            
        except Exception as e:
            return {
                "error": f"Failed to get usage data: {str(e)}",
                "ai_minutes_used": 0,
                "sms_count_used": 0,
                "ai_minutes_limit": 0,
                "sms_limit": 0,
                "can_use_ai": False,
                "can_send_sms": False
            }
    
    async def record_ai_usage(self, user_id: int, minutes_used: int, usage_date: Optional[date] = None, db: AsyncSession = None) -> bool:
        """Record AI usage for a user"""
        if usage_date is None:
            usage_date = date.today()
        
        try:
            # Use upsert to handle existing records
            from sqlalchemy.dialects.postgresql import insert
            
            stmt = insert(UserDailyUsage).values(
                user_id=user_id,
                usage_date=usage_date,
                ai_minutes_used=minutes_used,
                sms_count_used=0
            )
            
            # On conflict, update the ai_minutes_used
            stmt = stmt.on_conflict_do_update(
                index_elements=['user_id', 'usage_date'],
                set_=dict(
                    ai_minutes_used=stmt.excluded.ai_minutes_used + UserDailyUsage.ai_minutes_used,
                    updated_at=datetime.utcnow()
                )
            )
            
            await db.execute(stmt)
            await db.commit()
            return True
            
        except Exception as e:
            await db.rollback()
            return False
    
    async def record_sms_usage(self, user_id: int, sms_count: int = 1, usage_date: Optional[date] = None, db: AsyncSession = None) -> bool:
        """Record SMS usage for a user"""
        if usage_date is None:
            usage_date = date.today()
        
        try:
            # Use upsert to handle existing records
            from sqlalchemy.dialects.postgresql import insert
            
            stmt = insert(UserDailyUsage).values(
                user_id=user_id,
                usage_date=usage_date,
                ai_minutes_used=0,
                sms_count_used=sms_count
            )
            
            # On conflict, update the sms_count_used
            stmt = stmt.on_conflict_do_update(
                index_elements=['user_id', 'usage_date'],
                set_=dict(
                    sms_count_used=stmt.excluded.sms_count_used + UserDailyUsage.sms_count_used,
                    updated_at=datetime.utcnow()
                )
            )
            
            await db.execute(stmt)
            await db.commit()
            return True
            
        except Exception as e:
            await db.rollback()
            return False
    
    async def check_ai_usage_limit(self, user_id: int, requested_minutes: int, db: AsyncSession) -> Dict:
        """Check if user can use AI for the requested minutes"""
        usage_data = await self.get_user_daily_usage(user_id, date.today(), db)
        
        if "error" in usage_data:
            return {"allowed": False, "reason": usage_data["error"]}
        
        if not usage_data["can_use_ai"]:
            return {
                "allowed": False, 
                "reason": f"Daily AI limit reached ({usage_data['ai_minutes_used']}/{usage_data['ai_minutes_limit']} minutes used)"
            }
        
        # Check if the requested minutes would exceed the limit
        if usage_data["ai_minutes_limit"] < 999999:  # Not unlimited
            if usage_data["ai_minutes_used"] + requested_minutes > usage_data["ai_minutes_limit"]:
                remaining_minutes = usage_data["ai_minutes_limit"] - usage_data["ai_minutes_used"]
                return {
                    "allowed": False,
                    "reason": f"Requested {requested_minutes} minutes would exceed daily limit. Only {remaining_minutes} minutes remaining."
                }
        
        return {"allowed": True, "remaining_minutes": usage_data["ai_minutes_limit"] - usage_data["ai_minutes_used"]}
    
    async def check_sms_usage_limit(self, user_id: int, requested_sms: int = 1, db: AsyncSession = None) -> Dict:
        """Check if user can send SMS"""
        usage_data = await self.get_user_daily_usage(user_id, date.today(), db)
        
        if "error" in usage_data:
            return {"allowed": False, "reason": usage_data["error"]}
        
        if not usage_data["can_send_sms"]:
            return {
                "allowed": False, 
                "reason": f"Daily SMS limit reached ({usage_data['sms_count_used']}/{usage_data['sms_limit']} SMS used)"
            }
        
        # Check if the requested SMS would exceed the limit
        if usage_data["sms_limit"] < 999999:  # Not unlimited
            if usage_data["sms_count_used"] + requested_sms > usage_data["sms_limit"]:
                remaining_sms = usage_data["sms_limit"] - usage_data["sms_count_used"]
                return {
                    "allowed": False,
                    "reason": f"Requested {requested_sms} SMS would exceed daily limit. Only {remaining_sms} SMS remaining."
                }
        
        return {"allowed": True, "remaining_sms": usage_data["sms_limit"] - usage_data["sms_count_used"]}


# Import the UserDailyUsage model at module level for proper SQLAlchemy registration
from models.subscription import Base
from sqlalchemy import Column, Integer, Date, ForeignKey, DateTime
from sqlalchemy.sql import func

class UserDailyUsage(Base):
    __tablename__ = "user_daily_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    usage_date = Column(Date, nullable=False)
    ai_minutes_used = Column(Integer, default=0)
    sms_count_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())