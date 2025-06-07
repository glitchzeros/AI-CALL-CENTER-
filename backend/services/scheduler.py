"""
Background task scheduler for admin operations
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_database
from services.admin_service import AdminService

logger = logging.getLogger("aetherium.scheduler")


class AdminTaskScheduler:
    """Scheduler for admin background tasks"""
    
    def __init__(self):
        self.admin_service = AdminService()
        self.running = False
        self.tasks = {}
    
    async def start(self):
        """Start the scheduler"""
        if self.running:
            return
        
        self.running = True
        logger.info("🕐 Admin task scheduler started")
        
        # Schedule tasks
        self.tasks['cleanup_expired'] = asyncio.create_task(self._cleanup_expired_loop())
        self.tasks['update_modem_status'] = asyncio.create_task(self._update_modem_status_loop())
        self.tasks['usage_statistics'] = asyncio.create_task(self._usage_statistics_loop())
    
    async def stop(self):
        """Stop the scheduler"""
        if not self.running:
            return
        
        self.running = False
        
        # Cancel all tasks
        for task_name, task in self.tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                logger.info(f"Cancelled task: {task_name}")
        
        self.tasks.clear()
        logger.info("🛑 Admin task scheduler stopped")
    
    async def _cleanup_expired_loop(self):
        """Cleanup expired API key assignments every hour"""
        while self.running:
            try:
                async for db in get_database():
                    cleaned_count = await self.admin_service.cleanup_expired_assignments(db)
                    if cleaned_count > 0:
                        logger.info(f"🧹 Cleaned up {cleaned_count} expired API key assignments")
                    break
                
                # Wait 1 hour
                await asyncio.sleep(3600)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup expired loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _update_modem_status_loop(self):
        """Update modem status every 5 minutes"""
        while self.running:
            try:
                async for db in get_database():
                    updated_count = await self.admin_service.update_modem_status(db)
                    if updated_count > 0:
                        logger.info(f"📡 Updated status for {updated_count} modems")
                    break
                
                # Wait 5 minutes
                await asyncio.sleep(300)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in modem status update loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute on error
    
    async def _usage_statistics_loop(self):
        """Update usage statistics every 30 minutes"""
        while self.running:
            try:
                async for db in get_database():
                    await self._update_api_key_usage_stats(db)
                    await self._update_modem_usage_stats(db)
                    break
                
                # Wait 30 minutes
                await asyncio.sleep(1800)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in usage statistics loop: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes on error
    
    async def _update_api_key_usage_stats(self, db: AsyncSession):
        """Update API key usage statistics"""
        try:
            # Update daily usage counts
            query = """
                UPDATE gemini_api_keys 
                SET usage_count = (
                    SELECT COUNT(*) 
                    FROM api_key_usage 
                    WHERE api_key_id = gemini_api_keys.id 
                    AND timestamp >= CURRENT_DATE
                )
                WHERE status = 'assigned'
            """
            await db.execute(query)
            await db.commit()
            
            logger.debug("📊 Updated API key usage statistics")
            
        except Exception as e:
            logger.error(f"Failed to update API key usage stats: {e}")
            await db.rollback()
    
    async def _update_modem_usage_stats(self, db: AsyncSession):
        """Update modem usage statistics"""
        try:
            # Update modem uptime and call statistics
            query = """
                UPDATE gsm_modems 
                SET last_seen_at = CURRENT_TIMESTAMP
                WHERE status = 'online'
            """
            await db.execute(query)
            await db.commit()
            
            logger.debug("📊 Updated modem usage statistics")
            
        except Exception as e:
            logger.error(f"Failed to update modem usage stats: {e}")
            await db.rollback()


# Global scheduler instance
admin_scheduler = AdminTaskScheduler()


async def start_admin_scheduler():
    """Start the admin task scheduler"""
    await admin_scheduler.start()


async def stop_admin_scheduler():
    """Stop the admin task scheduler"""
    await admin_scheduler.stop()