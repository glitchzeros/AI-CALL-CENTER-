"""
Payment Monitoring Service
The Scribe's Payment Watcher
"""

import logging
import asyncio
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from database.connection import get_database
from models.sms_verification import PaymentMonitoringSession
from models.user import User
from models.subscription import SubscriptionTier
from models.modem import GSMModem, SMSMessage
from services.sms_service import SMSService

logger = logging.getLogger(__name__)

class PaymentMonitoringService:
    """Service for monitoring payment confirmations via SMS"""
    
    def __init__(self):
        self.monitoring_sessions = {}  # In-memory tracking of active sessions
        self.sms_service = SMSService()
        logger.info("💰 Payment monitoring service initialized")
    
    async def start_payment_monitoring(
        self,
        user_id: int,
        subscription_tier_id: int,
        company_number: str,
        bank_card_number: str,
        amount_usd: float,
        amount_uzs: int,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Start monitoring payment for a subscription
        
        Args:
            user_id: User ID
            subscription_tier_id: Subscription tier ID
            company_number: Company phone number to monitor
            bank_card_number: Bank card number for payment
            amount_usd: Amount in USD
            amount_uzs: Amount in UZS
            db: Database session
            
        Returns:
            Payment monitoring session details
        """
        try:
            # Generate unique reference code
            reference_code = f"AET{secrets.randbelow(900000) + 100000:06d}"
            
            # Create monitoring session
            monitoring_session = PaymentMonitoringSession(
                user_id=user_id,
                subscription_tier_id=subscription_tier_id,
                company_number=company_number,
                bank_card_number=bank_card_number,
                amount_usd=amount_usd,
                amount_uzs=amount_uzs,
                reference_code=reference_code,
                status="monitoring",
                started_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(minutes=30),
                last_sms_check=datetime.utcnow()
            )
            
            db.add(monitoring_session)
            await db.commit()
            await db.refresh(monitoring_session)
            
            # Start background monitoring task
            asyncio.create_task(self._monitor_payment_session(monitoring_session.id))
            
            logger.info(f"Payment monitoring started for user {user_id}, reference: {reference_code}")
            
            return {
                "session_id": monitoring_session.id,
                "reference_code": reference_code,
                "company_number": company_number,
                "bank_card_number": bank_card_number,
                "amount_usd": amount_usd,
                "amount_uzs": amount_uzs,
                "expires_at": monitoring_session.expires_at.isoformat(),
                "monitoring_duration_minutes": 30
            }
            
        except Exception as e:
            logger.error(f"Error starting payment monitoring: {e}")
            await db.rollback()
            raise
    
    async def _monitor_payment_session(self, session_id: int):
        """
        Background task to monitor payment session
        
        Args:
            session_id: Payment monitoring session ID
        """
        try:
            while True:
                # Use proper session management
                from database.connection import AsyncSessionLocal
                async with AsyncSessionLocal() as db:
                    try:
                        # Get monitoring session
                        result = await db.execute(
                            select(PaymentMonitoringSession).where(
                                PaymentMonitoringSession.id == session_id
                            )
                        )
                        session = result.scalar_one_or_none()
                        
                        if not session:
                            logger.warning(f"Payment monitoring session {session_id} not found")
                            return
                        
                        # Check if session expired
                        if datetime.utcnow() > session.expires_at:
                            await self._expire_payment_session(session, db)
                            return
                        
                        # Check if already confirmed
                        if session.status == "confirmed":
                            logger.info(f"Payment session {session_id} already confirmed")
                            return
                        
                        # Check for new SMS messages
                        await self._check_payment_sms(session, db)
                        
                        # Update last check time
                        session.last_sms_check = datetime.utcnow()
                        await db.commit()
                        
                    except Exception as e:
                        logger.error(f"Error in payment monitoring iteration: {e}")
                        await db.rollback()
                        raise
                
                # Wait 1 minute before next check
                await asyncio.sleep(60)
                
        except asyncio.CancelledError:
            logger.info(f"Payment monitoring cancelled for session {session_id}")
        except Exception as e:
            logger.error(f"Error in payment monitoring task: {e}")
    
    async def _check_payment_sms(self, session: PaymentMonitoringSession, db: AsyncSession):
        """
        Check for payment confirmation SMS
        
        Args:
            session: Payment monitoring session
            db: Database session
        """
        try:
            # Get GSM modem for the company number
            modem_result = await db.execute(
                select(GSMModem).where(GSMModem.phone_number == session.company_number)
            )
            modem = modem_result.scalar_one_or_none()
            
            if not modem:
                logger.warning(f"No GSM modem found for company number {session.company_number}")
                return
            
            # Check for new SMS messages since last check
            sms_result = await db.execute(
                select(SMSMessage).where(
                    (SMSMessage.modem_id == modem.id) &
                    (SMSMessage.direction == "incoming") &
                    (SMSMessage.received_at > session.last_sms_check)
                )
            )
            new_messages = sms_result.scalars().all()
            
            for message in new_messages:
                if await self._analyze_payment_sms(message.content, session):
                    await self._confirm_payment(session, message.content, db)
                    return
                    
        except Exception as e:
            logger.error(f"Error checking payment SMS: {e}")
    
    async def _analyze_payment_sms(self, sms_content: str, session: PaymentMonitoringSession) -> bool:
        """
        Analyze SMS content for payment confirmation
        
        Args:
            sms_content: SMS message content
            session: Payment monitoring session
            
        Returns:
            True if payment is confirmed
        """
        try:
            # Convert to lowercase for analysis
            content_lower = sms_content.lower()
            
            # Check for payment keywords
            payment_keywords = [
                "перевод", "перечисление", "оплата", "платеж", "зачисление",
                "transfer", "payment", "paid", "received", "credited"
            ]
            
            # Check for amount in UZS
            amount_str = str(session.amount_uzs)
            
            # Check for card number (last 4 digits)
            card_last_digits = session.bank_card_number[-4:] if session.bank_card_number else ""
            
            # Check for reference code
            reference_code = session.reference_code
            
            # Simple analysis - look for keywords and amount
            has_payment_keyword = any(keyword in content_lower for keyword in payment_keywords)
            has_amount = amount_str in sms_content
            has_card_digits = card_last_digits in sms_content if card_last_digits else False
            has_reference = reference_code.lower() in content_lower
            
            # Confirm if we have payment keyword and either amount, card digits, or reference
            is_confirmed = has_payment_keyword and (has_amount or has_card_digits or has_reference)
            
            logger.info(f"SMS analysis for session {session.id}: "
                       f"payment_keyword={has_payment_keyword}, amount={has_amount}, "
                       f"card_digits={has_card_digits}, reference={has_reference}, "
                       f"confirmed={is_confirmed}")
            
            return is_confirmed
            
        except Exception as e:
            logger.error(f"Error analyzing payment SMS: {e}")
            return False
    
    async def _confirm_payment(
        self,
        session: PaymentMonitoringSession,
        sms_content: str,
        db: AsyncSession
    ):
        """
        Confirm payment and activate subscription
        
        Args:
            session: Payment monitoring session
            sms_content: Confirming SMS content
            db: Database session
        """
        try:
            # Update session status
            session.status = "confirmed"
            session.confirmed_at = datetime.utcnow()
            session.sms_content = sms_content
            
            # Here you would typically:
            # 1. Create/update user subscription
            # 2. Send confirmation notification
            # 3. Log the successful payment
            
            await db.commit()
            
            logger.info(f"Payment confirmed for session {session.id}, user {session.user_id}")
            
            # TODO: Implement subscription activation logic
            
        except Exception as e:
            logger.error(f"Error confirming payment: {e}")
            await db.rollback()
    
    async def _expire_payment_session(
        self,
        session: PaymentMonitoringSession,
        db: AsyncSession
    ):
        """
        Expire payment monitoring session
        
        Args:
            session: Payment monitoring session
            db: Database session
        """
        try:
            session.status = "expired"
            await db.commit()
            
            logger.info(f"Payment session {session.id} expired for user {session.user_id}")
            
        except Exception as e:
            logger.error(f"Error expiring payment session: {e}")
            await db.rollback()
    
    async def get_active_payment_session(self, user_id: int, db: AsyncSession) -> Optional[Dict[str, Any]]:
        """
        Get active payment monitoring session for user
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            Active payment session details or None
        """
        try:
            result = await db.execute(
                select(PaymentMonitoringSession).where(
                    (PaymentMonitoringSession.user_id == user_id) &
                    (PaymentMonitoringSession.status == "monitoring") &
                    (PaymentMonitoringSession.expires_at > datetime.utcnow())
                )
            )
            session = result.scalar_one_or_none()
            
            if session:
                return {
                    "session_id": session.id,
                    "reference_code": session.reference_code,
                    "company_number": session.company_number,
                    "bank_card_number": session.bank_card_number,
                    "amount_usd": float(session.amount_usd),
                    "amount_uzs": int(session.amount_uzs),
                    "expires_at": session.expires_at.isoformat(),
                    "time_remaining_seconds": int((session.expires_at - datetime.utcnow()).total_seconds())
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting active payment session: {e}")
            return None