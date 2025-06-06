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
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_database():
    """
    Initialize database connection and verify schema
    """
    try:
        async with engine.begin() as conn:
            # Test connection
            result = await conn.execute(text("SELECT 1"))
            logger.info("✅ Database connection established")
            
            # Verify key tables exist
            tables_check = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('users', 'subscription_tiers', 'scribe_workflows')
            """))
            
            tables = [row[0] for row in tables_check.fetchall()]
            
            if len(tables) >= 3:
                logger.info("✅ Database schema verified")
            else:
                logger.warning(f"⚠️ Database schema incomplete. Found tables: {tables}")
                
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise

async def close_database():
    """
    Close database connections
    """
    await engine.dispose()
    logger.info("🔒 Database connections closed")