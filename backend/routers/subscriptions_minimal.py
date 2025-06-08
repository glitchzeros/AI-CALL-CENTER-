"""
Minimal subscriptions router - only tiers endpoint
Isolated to avoid SQLAlchemy relationship issues
"""

from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from pydantic import BaseModel
from typing import List
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

router = APIRouter()

class SubscriptionTierResponse(BaseModel):
    id: int
    name: str
    display_name: str
    description: str
    price_usd: float
    price_uzs: int
    max_daily_ai_minutes: int
    max_daily_sms: int
    context_limit: int
    has_agentic_functions: bool
    has_agentic_constructor: bool
    features: str

@router.get("/test")
async def test_endpoint():
    """Test endpoint to verify routing works"""
    return {"status": "success", "message": "Routing works!"}

@router.get("/tiers", response_model=List[SubscriptionTierResponse])
async def get_subscription_tiers():
    """
    Get available subscription tiers
    The Scribe's Service Offerings
    """
    try:
        print("🔍 Starting subscription tiers endpoint")
        # Create completely isolated database connection
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
                    display_name=row.name.replace('_', ' ').title(),
                    description=row.description or "",
                    price_usd=float(row.price_usd or 0),
                    price_uzs=row.price_uzs,
                    max_daily_ai_minutes=row.max_daily_ai_minutes,
                    max_daily_sms=row.max_daily_sms,
                    context_limit=row.context_limit,
                    has_agentic_functions=row.has_agentic_functions,
                    has_agentic_constructor=row.has_agentic_constructor,
                    features="[]"
                )
                for row in rows
            ]
            
    except Exception as e:
        print(f"Subscription tiers error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get subscription tiers: {str(e)}")