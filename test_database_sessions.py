#!/usr/bin/env python3
"""
Test script to validate database session management fixes
"""

import asyncio
import sys
import os
import logging

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database.connection import get_database, init_database, AsyncSessionLocal
from sqlalchemy import text

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_get_database_dependency():
    """Test the get_database dependency function"""
    logger.info("Testing get_database dependency...")
    
    try:
        async for db in get_database():
            # Test a simple query
            result = await db.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            logger.info(f"✅ get_database dependency test passed: {row}")
            break
    except Exception as e:
        logger.error(f"❌ get_database dependency test failed: {e}")
        return False
    
    return True

async def test_direct_session_usage():
    """Test direct session usage pattern"""
    logger.info("Testing direct session usage...")
    
    try:
        async with AsyncSessionLocal() as db:
            # Test a simple query
            result = await db.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            logger.info(f"✅ Direct session usage test passed: {row}")
    except Exception as e:
        logger.error(f"❌ Direct session usage test failed: {e}")
        return False
    
    return True

async def test_multiple_concurrent_sessions():
    """Test multiple concurrent sessions"""
    logger.info("Testing multiple concurrent sessions...")
    
    async def session_task(task_id):
        try:
            async with AsyncSessionLocal() as db:
                result = await db.execute(text(f"SELECT {task_id} as task_id"))
                row = result.fetchone()
                logger.info(f"✅ Task {task_id} completed: {row}")
                return True
        except Exception as e:
            logger.error(f"❌ Task {task_id} failed: {e}")
            return False
    
    # Run 5 concurrent sessions
    tasks = [session_task(i) for i in range(1, 6)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    success_count = sum(1 for result in results if result is True)
    logger.info(f"Concurrent sessions test: {success_count}/5 succeeded")
    
    return success_count == 5

async def test_error_handling():
    """Test error handling in sessions"""
    logger.info("Testing error handling...")
    
    try:
        async with AsyncSessionLocal() as db:
            # This should cause an error
            await db.execute(text("SELECT * FROM non_existent_table"))
    except Exception as e:
        logger.info(f"✅ Error handling test passed - caught expected error: {type(e).__name__}")
        return True
    
    logger.error("❌ Error handling test failed - no error was raised")
    return False

async def main():
    """Run all tests"""
    logger.info("🧪 Starting database session management tests...")
    
    try:
        # Initialize database
        await init_database()
        logger.info("✅ Database initialized")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False
    
    tests = [
        ("get_database dependency", test_get_database_dependency),
        ("direct session usage", test_direct_session_usage),
        ("multiple concurrent sessions", test_multiple_concurrent_sessions),
        ("error handling", test_error_handling),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n--- Running {test_name} test ---")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "="*50)
    logger.info("TEST SUMMARY")
    logger.info("="*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        logger.info("🎉 All database session tests passed!")
        return True
    else:
        logger.error("💥 Some database session tests failed!")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)