#!/usr/bin/env python3
"""
Direct test of subscription tiers endpoint
Bypasses FastAPI to test database connectivity
"""

import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

async def test_subscription_tiers():
    """Test subscription tiers query directly"""
    try:
        DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+asyncpg://demo_user:aetherium_demo@database:5432/aetherium_demo')
        print(f"🔗 Connecting to: {DATABASE_URL}")
        
        engine = create_async_engine(DATABASE_URL)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as db:
            print("✅ Database session created")
            
            # Use raw SQL to avoid SQLAlchemy relationship issues
            query = text("""
                SELECT id, name, description, price_usd, price_uzs, 
                       max_daily_ai_minutes, max_daily_sms, context_limit,
                       has_agentic_functions, has_agentic_constructor
                FROM subscription_tiers 
                ORDER BY price_usd
            """)
            
            result = await db.execute(query)
            rows = result.fetchall()
            
            print(f"✅ Found {len(rows)} subscription tiers:")
            for row in rows:
                print(f"  - {row.name}: ${row.price_usd} USD / {row.price_uzs} UZS")
                print(f"    Description: {row.description}")
                print(f"    AI Minutes: {row.max_daily_ai_minutes}, SMS: {row.max_daily_sms}")
                print(f"    Context: {row.context_limit}, Agentic: {row.has_agentic_functions}")
                print()
            
            # Format as API response
            tiers = []
            for row in rows:
                tier = {
                    "id": row.id,
                    "name": row.name,
                    "display_name": row.name.replace('_', ' ').title(),
                    "description": row.description or "",
                    "price_usd": float(row.price_usd or 0),
                    "price_uzs": row.price_uzs,
                    "max_daily_ai_minutes": row.max_daily_ai_minutes,
                    "max_daily_sms": row.max_daily_sms,
                    "context_limit": row.context_limit,
                    "has_agentic_functions": row.has_agentic_functions,
                    "has_agentic_constructor": row.has_agentic_constructor,
                    "features": "[]"
                }
                tiers.append(tier)
            
            print("🎯 API Response format:")
            import json
            print(json.dumps(tiers, indent=2))
            
            return tiers
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    asyncio.run(test_subscription_tiers())