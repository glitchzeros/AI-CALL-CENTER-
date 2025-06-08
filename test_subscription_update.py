#!/usr/bin/env python3
"""
Test script for the updated subscription system
"""

import asyncio
import sys
import os
sys.path.append('/workspace/AI-CALL-CENTER-/backend')

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
from models.subscription import SubscriptionTier
from services.usage_tracking_service import UsageTrackingService

# Database configuration
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/aetherium"

async def test_subscription_system():
    """Test the updated subscription system"""
    
    # Create async engine
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        try:
            print("🔍 Testing subscription system...")
            
            # Test 1: Check if new subscription tiers exist
            print("\n1. Checking subscription tiers...")
            result = await session.execute(select(SubscriptionTier))
            tiers = result.scalars().all()
            
            print(f"Found {len(tiers)} subscription tiers:")
            for tier in tiers:
                print(f"  - {tier.name}: {tier.display_name}")
                print(f"    Price: {tier.price_uzs:,} UZS (${tier.price_usd} USD)")
                print(f"    Daily AI Minutes: {tier.max_daily_ai_minutes}")
                print(f"    Daily SMS: {tier.max_daily_sms}")
                print(f"    Agentic Functions: {tier.has_agentic_functions}")
                print(f"    Agentic Constructor: {tier.has_agentic_constructor}")
                print()
            
            # Test 2: Check if user_daily_usage table exists
            print("2. Checking user_daily_usage table...")
            try:
                result = await session.execute(text("SELECT COUNT(*) FROM user_daily_usage"))
                count = result.scalar()
                print(f"✅ user_daily_usage table exists with {count} records")
            except Exception as e:
                print(f"❌ user_daily_usage table issue: {e}")
            
            # Test 3: Test usage tracking service
            print("\n3. Testing usage tracking service...")
            usage_service = UsageTrackingService()
            
            # Test with a dummy user ID (assuming user 1 exists)
            from datetime import date
            usage_data = await usage_service.get_user_daily_usage(1, date.today(), session)
            print(f"Usage data for user 1: {usage_data}")
            
            print("\n✅ Subscription system test completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during testing: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_subscription_system())