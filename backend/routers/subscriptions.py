"""
Subscriptions router
The Scribe's Service Tiers
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from pydantic import BaseModel
from typing import List, Optional

# from database.connection import get_database  # Temporarily disabled to avoid relationship issues
# Temporarily avoid importing models that have relationship issues
# from models.user import User
# from models.subscription import SubscriptionTier
# from routers.auth import get_current_user  # Temporarily disabled to avoid User model import
# from services.manual_payment_service import ManualPaymentService
# from services.payment_monitoring_service import PaymentMonitoringService
# from services.usage_tracking_service import UsageTrackingService

router = APIRouter()

@router.get("/test")
async def test_endpoint():
    """Simple test endpoint with no dependencies"""
    return {"message": "Subscription router is working", "status": "ok"}

class SubscriptionTierResponse(BaseModel):
    id: int
    name: str
    display_name: Optional[str] = None  # Will be populated from name
    description: Optional[str]
    price_usd: float
    price_uzs: Optional[int]
    max_daily_ai_minutes: Optional[int]
    max_daily_sms: Optional[int]
    context_limit: Optional[int]
    has_agentic_functions: Optional[bool]
    has_agentic_constructor: Optional[bool]
    features: Optional[str]

class PaymentInitiation(BaseModel):
    tier_id: int

class PaymentMonitoringRequest(BaseModel):
    tier_id: int
    bank_card_number: str

@router.get("/tiers", response_model=List[SubscriptionTierResponse])
async def get_subscription_tiers():
    """
    Get available subscription tiers
    The Scribe's Service Offerings
    """
    try:
        print("🔍 Starting subscription tiers endpoint")
        # Create completely isolated database connection to avoid SQLAlchemy relationship issues
        import os
        from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
        from sqlalchemy.orm import sessionmaker
        
        DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://demo_user:aetherium_demo@database:5432/aetherium_demo')
        print(f"🔍 Using DATABASE_URL: {DATABASE_URL}")
        engine = create_async_engine(DATABASE_URL)
        print("🔍 Engine created")
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        print("🔍 Session maker created")
        
        async with async_session() as db:
            print("🔍 Database session created")
            # Use raw SQL to avoid SQLAlchemy relationship issues
            query = text("""
                SELECT id, name, description, price_usd, price_uzs, 
                       max_daily_ai_minutes, max_daily_sms, context_limit,
                       has_agentic_functions, has_agentic_constructor
                FROM subscription_tiers 
                ORDER BY price_usd
            """)
            print("🔍 Query prepared")
            
            result = await db.execute(query)
            print("🔍 Query executed")
            rows = result.fetchall()
            print(f"🔍 Got {len(rows)} rows")
            
            return [
                SubscriptionTierResponse(
                    id=row.id,
                    name=row.name,
                    display_name=row.name.replace('_', ' ').title(),  # Convert name to display name
                    description=row.description or "",
                    price_usd=float(row.price_usd or 0),
                    price_uzs=row.price_uzs,
                    max_daily_ai_minutes=row.max_daily_ai_minutes,
                    max_daily_sms=row.max_daily_sms,
                    context_limit=row.context_limit,
                    has_agentic_functions=row.has_agentic_functions,
                    has_agentic_constructor=row.has_agentic_constructor,
                    features="[]"  # Default empty features
                )
                for row in rows
            ]
        
    except Exception as e:
        import traceback
        error_details = f"Error: {str(e)}\nTraceback: {traceback.format_exc()}"
        print(f"Subscription tiers error: {error_details}")  # This will show in logs
        raise HTTPException(status_code=500, detail=f"Failed to get subscription tiers: {str(e)}")

# Temporarily disabled to avoid get_database dependency issues
# @router.post("/initiate-payment")
# async def initiate_payment(
#     payment_data: PaymentInitiation,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_database)
# ):
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
        
        # Initiate manual payment
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

# Temporarily disabled to avoid get_database dependency issues
# @router.post("/start-payment-monitoring")
# async def start_payment_monitoring(
#     payment_data: PaymentMonitoringRequest,
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_database)
# ):
#     """
#     Start payment monitoring with 30-minute timer
#     The Scribe's Payment Watcher Activation
#     """
#     try:
#         # Get tier information
#         tier_result = await db.execute(
#             select(SubscriptionTier).where(SubscriptionTier.id == payment_data.tier_id)
#         )
#         tier = tier_result.scalar_one_or_none()
#         
#         if not tier:
#             raise HTTPException(status_code=404, detail="Subscription tier not found")
#         
#         if not current_user.company_number:
#             raise HTTPException(status_code=400, detail="User has no assigned company number")
#         
#         # Calculate amounts - use UZS pricing directly
#         amount_usd = float(tier.price_usd)
#         amount_uzs = tier.price_uzs  # Use direct UZS pricing
#         
#         # Start payment monitoring
#         monitoring_service = PaymentMonitoringService()
#         result = await monitoring_service.start_payment_monitoring(
#             user_id=current_user.id,
#             subscription_tier_id=tier.id,
#             company_number=current_user.company_number,
#             bank_card_number=payment_data.bank_card_number,
#             amount_usd=amount_usd,
#             amount_uzs=amount_uzs,
#             db=db
#         )
#         
#         return {
#             "success": True,
#             "message": "Payment monitoring started. Transfer money to the specified card and we'll monitor for confirmation SMS.",
#             "monitoring_session": result,
#             "tier_name": tier.name,
#             "instructions": f"Transfer {amount_uzs:,} UZS to card {payment_data.bank_card_number} with reference {result['reference_code']}"
#         }
#         
#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Failed to start payment monitoring")

# Temporarily disabled to avoid get_database dependency issues
# @router.get("/payment-monitoring-status")
# async def get_payment_monitoring_status(
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_database)
# ):
#     """
#     Get current payment monitoring status
#     The Scribe's Payment Status Check
#     """
#     try:
#         monitoring_service = PaymentMonitoringService()
#         session = await monitoring_service.get_active_payment_session(current_user.id, db)
#         
#         if session:
#             return {
#                 "has_active_session": True,
#                 "session": session
#             }
#         else:
#             return {
#                 "has_active_session": False,
#                 "session": None
#             }
#         
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Failed to get payment monitoring status")

# Temporarily disabled to avoid get_database dependency issues
# @router.get("/usage-status")
# async def get_usage_status(
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_database)
# ):
#     """
#     Get current user's daily usage status
#     The Scribe's Usage Tracker
#     """
#     try:
#         from datetime import date
#         usage_service = UsageTrackingService()
#         usage_data = await usage_service.get_user_daily_usage(
#             user_id=current_user.id,
#             usage_date=date.today(),
#             db=db
#         )
#         
#         return {
#             "success": True,
#             "usage_data": usage_data,
#             "date": date.today().isoformat()
#         }
#         
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Failed to get usage status")

# Temporarily disabled to avoid get_database dependency issues
# @router.get("/my-subscription")
# async def get_my_subscription(
#     current_user: User = Depends(get_current_user),
#     db: AsyncSession = Depends(get_database)
# ):
#     """
#     Get current user's subscription details
#     The Scribe's Membership Status
#     """
#     try:
#         from models.subscription import UserSubscription
#         from sqlalchemy import and_
#         
#         # Get user's current subscription
#         result = await db.execute(
#             select(UserSubscription, SubscriptionTier)
#             .join(SubscriptionTier)
#             .where(
#                 and_(
#                     UserSubscription.user_id == current_user.id,
#                     UserSubscription.status == 'active'
#                 )
#             )
#         )
#         subscription_data = result.first()
#         
#         if not subscription_data:
#             return {
#                 "has_subscription": False,
#                 "subscription": None,
#                 "tier": None
#             }
#         
#         subscription, tier = subscription_data
#         
#         # Get usage data
#         from datetime import date
#         usage_service = UsageTrackingService()
#         usage_data = await usage_service.get_user_daily_usage(
#             user_id=current_user.id,
#             usage_date=date.today(),
#             db=db
#         )
#         
#         return {
#             "has_subscription": True,
#             "subscription": {
#                 "id": subscription.id,
#                 "status": subscription.status,
#                 "started_at": subscription.started_at.isoformat() if subscription.started_at else None,
#                 "expires_at": subscription.expires_at.isoformat() if subscription.expires_at else None,
#                 "auto_renew": subscription.auto_renew
#             },
#             "tier": {
#                 "id": tier.id,
#                 "name": tier.name,
#                 "display_name": tier.display_name,
#                 "description": tier.description,
#                 "price_uzs": tier.price_uzs,
#                 "max_daily_ai_minutes": tier.max_daily_ai_minutes,
#                 "max_daily_sms": tier.max_daily_sms,
#                 "has_agentic_functions": tier.has_agentic_functions,
#                 "has_agentic_constructor": tier.has_agentic_constructor
#             },
#             "usage": usage_data
#         }
#         
#     except Exception as e:
#         raise HTTPException(status_code=500, detail="Failed to get subscription details")