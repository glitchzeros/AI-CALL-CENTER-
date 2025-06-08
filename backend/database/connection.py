"""
Database connection and session management
The Scribe's Memory Palace Gateway
"""

import os
import logging
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://aetherium_user:aetherium_secure_pass_2024@localhost:5432/aetherium"
)

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL debugging
    pool_size=20,
    max_overflow=30,
    pool_pre_ping=True,
    pool_recycle=3600
)

# Create session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()

async def get_database() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to get database session
    """
    session = None
    try:
        print("DEBUG: Creating AsyncSessionLocal...")
        session = AsyncSessionLocal()
        print("DEBUG: Session created, yielding...")
        yield session
        print("DEBUG: After yield, committing...")
        await session.commit()
        print("DEBUG: Commit successful")
    except Exception as e:
        import traceback
        error_details = f"Database session error during operation: {e}\nTraceback: {traceback.format_exc()}"
        logger.error(error_details)
        print(f"FULL ERROR: {error_details}")  # This will show in container logs
        if session:
            try:
                await session.rollback()
            except Exception as rollback_error:
                logger.error(f"Error during rollback: {rollback_error}")
        raise
    finally:
        if session:
            try:
                await session.close()
            except Exception as close_error:
                logger.error(f"Error closing session: {close_error}")

async def init_database():
    """
    Initialize database connection and verify schema
    """
    try:
        async with engine.begin() as conn:
            # Test connection
            result = await conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection established")
            
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("✅ Database schema initialized")
                
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

async def close_database():
    """
    Close database connections
    """
    await engine.dispose()
    logger.info("🔒 Database connections closed")