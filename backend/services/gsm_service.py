"""
GSM Module Management Service
The Scribe's Communication Device Manager
"""

import logging
import asyncio
import secrets
import httpx
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from models.gsm_module import GSMModule, PaymentSession
from models.sms_verification import SMSVerificationSession
from models.user import User

logger = logging.getLogger(__name__)

class GSMService:
    """Service for managing GSM modules and SMS verification"""
    
    def __init__(self):
        self.modem_manager_url = "http://modem-manager:8001"
        logger.info("📱 GSM service initialized")
    
    async def get_available_gsm_module(self, db: AsyncSession) -> Optional[GSMModule]:
        """Get an available GSM module for sending SMS"""
        try:
            result = await db.execute(
                select(GSMModule)
                .where(
                    and_(
                        GSMModule.is_active == True,
                        GSMModule.is_available == True,
                        GSMModule.status == "idle"
                    )
                )
                .order_by(GSMModule.priority.desc(), GSMModule.last_used_at.asc())
                .limit(1)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting available GSM module: {e}")
            return None
    
    async def create_sms_verification_session(
        self,
        db: AsyncSession,
        user_id: int,
        phone_number: str,
        session_type: str = "login"
    ) -> SMSVerificationSession:
        """Create SMS verification session"""
        try:
            # Generate verification code
            verification_code = f"{secrets.randbelow(900000) + 100000:06d}"
            
            # Get available GSM module
            gsm_module = await self.get_available_gsm_module(db)
            
            # Create verification session
            session = SMSVerificationSession(
                user_id=user_id,
                phone_number=phone_number,
                verification_code=verification_code,
                gsm_module_id=gsm_module.id if gsm_module else None,
                session_type=session_type,
                expires_at=datetime.utcnow() + timedelta(minutes=10),
                is_demo=gsm_module is None  # Demo mode if no GSM module available
            )
            
            db.add(session)
            await db.commit()
            await db.refresh(session)
            
            # Send SMS if GSM module is available
            if gsm_module:
                await self._send_verification_sms(session, gsm_module)
                
                # Mark GSM module as busy temporarily
                gsm_module.is_available = False
                gsm_module.last_used_at = datetime.utcnow()
                await db.commit()
                
                # Release GSM module after a short delay
                asyncio.create_task(self._release_gsm_module(db, gsm_module.id))
            else:
                logger.warning(f"No GSM modules available, using demo mode for user {user_id}")
            
            return session
            
        except Exception as e:
            logger.error(f"Error creating SMS verification session: {e}")
            await db.rollback()
            raise
    
    async def _send_verification_sms(self, session: SMSVerificationSession, gsm_module: GSMModule):
        """Send verification SMS through GSM module"""
        try:
            message = f"Ваш код подтверждения Aetherium: {session.verification_code}. Код действителен 10 минут."
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.modem_manager_url}/send-sms",
                    json={
                        "to_number": session.phone_number,
                        "content": message,
                        "from_number": gsm_module.phone_number,
                        "priority": "high"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    logger.info(f"Verification SMS sent to {session.phone_number} via {gsm_module.phone_number}")
                else:
                    logger.error(f"Failed to send SMS: {response.status_code} - {response.text}")
                    
        except Exception as e:
            logger.error(f"Error sending verification SMS: {e}")
    
    async def _release_gsm_module(self, db: AsyncSession, gsm_module_id: int):
        """Release GSM module after sending SMS"""
        try:
            await asyncio.sleep(5)  # Wait 5 seconds before releasing
            
            async with db() as session:
                result = await session.execute(
                    select(GSMModule).where(GSMModule.id == gsm_module_id)
                )
                gsm_module = result.scalar_one_or_none()
                
                if gsm_module:
                    gsm_module.is_available = True
                    await session.commit()
                    logger.info(f"Released GSM module {gsm_module_id}")
                    
        except Exception as e:
            logger.error(f"Error releasing GSM module {gsm_module_id}: {e}")
    
    async def verify_sms_code(
        self,
        db: AsyncSession,
        user_id: int,
        verification_code: str,
        session_type: str = "login"
    ) -> bool:
        """Verify SMS code"""
        try:
            # Find active verification session
            result = await db.execute(
                select(SMSVerificationSession)
                .where(
                    and_(
                        SMSVerificationSession.user_id == user_id,
                        SMSVerificationSession.session_type == session_type,
                        SMSVerificationSession.status == "pending",
                        SMSVerificationSession.expires_at > datetime.utcnow()
                    )
                )
                .order_by(SMSVerificationSession.created_at.desc())
                .limit(1)
            )
            session = result.scalar_one_or_none()
            
            if not session:
                logger.warning(f"No active SMS verification session found for user {user_id}")
                return False
            
            # Check verification code
            if session.verification_code == verification_code:
                session.status = "verified"
                session.verified_at = datetime.utcnow()
                await db.commit()
                
                logger.info(f"SMS verification successful for user {user_id}")
                return True
            else:
                session.attempts += 1
                
                if session.attempts >= session.max_attempts:
                    session.status = "failed"
                
                await db.commit()
                logger.warning(f"Invalid SMS verification code for user {user_id}")
                return False
                
        except Exception as e:
            logger.error(f"Error verifying SMS code: {e}")
            return False
    
    async def get_demo_code(self, db: AsyncSession, user_id: int) -> Optional[str]:
        """Get demo verification code when no GSM modules are available"""
        try:
            result = await db.execute(
                select(SMSVerificationSession)
                .where(
                    and_(
                        SMSVerificationSession.user_id == user_id,
                        SMSVerificationSession.status == "pending",
                        SMSVerificationSession.is_demo == True,
                        SMSVerificationSession.expires_at > datetime.utcnow()
                    )
                )
                .order_by(SMSVerificationSession.created_at.desc())
                .limit(1)
            )
            session = result.scalar_one_or_none()
            
            if session:
                session.demo_code_shown = True
                await db.commit()
                return session.verification_code
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting demo code: {e}")
            return None
    
    async def create_payment_session(
        self,
        db: AsyncSession,
        user_id: int,
        subscription_tier: str,
        amount_usd: int
    ) -> PaymentSession:
        """Create payment session with GSM module assignment"""
        try:
            # Get available GSM module
            gsm_module = await self.get_available_gsm_module(db)
            
            if not gsm_module:
                raise ValueError("No GSM modules available for payment processing")
            
            # Calculate UZS amount (1 USD = 12300 UZS)
            amount_uzs = amount_usd * 12300
            
            # Create payment session
            session = PaymentSession(
                user_id=user_id,
                gsm_module_id=gsm_module.id,
                subscription_tier=subscription_tier,
                amount_uzs=amount_uzs,
                amount_usd=amount_usd,
                bank_card_number=gsm_module.bank_card_number,
                bank_name=gsm_module.bank_name,
                card_holder_name=gsm_module.card_holder_name,
                expires_at=datetime.utcnow() + timedelta(minutes=30)
            )
            
            db.add(session)
            await db.commit()
            await db.refresh(session)
            
            logger.info(f"Created payment session {session.id} for user {user_id}")
            return session
            
        except Exception as e:
            logger.error(f"Error creating payment session: {e}")
            await db.rollback()
            raise
    
    async def check_payment_confirmation(
        self,
        db: AsyncSession,
        sms_content: str,
        sender_number: str,
        company_number: str
    ) -> Dict[str, Any]:
        """Check if SMS is a payment confirmation"""
        try:
            # Find GSM module by phone number
            result = await db.execute(
                select(GSMModule).where(GSMModule.phone_number == company_number)
            )
            gsm_module = result.scalar_one_or_none()
            
            if not gsm_module:
                return {"success": False, "error": "GSM module not found"}
            
            # Find active payment sessions for this GSM module
            result = await db.execute(
                select(PaymentSession)
                .options(selectinload(PaymentSession.user))
                .where(
                    and_(
                        PaymentSession.gsm_module_id == gsm_module.id,
                        PaymentSession.status == "pending",
                        PaymentSession.expires_at > datetime.utcnow()
                    )
                )
                .order_by(PaymentSession.created_at.desc())
            )
            payment_sessions = result.scalars().all()
            
            # Analyze SMS content for payment confirmation
            confirmation_result = await self._analyze_payment_sms(sms_content, payment_sessions)
            
            if confirmation_result.get("confirmed"):
                session = confirmation_result["session"]
                session.status = "confirmed"
                session.confirmed_at = datetime.utcnow()
                session.confirmation_sms = sms_content
                session.confirmation_amount = confirmation_result.get("amount")
                
                await db.commit()
                
                logger.info(f"Payment confirmed for session {session.id}")
                
                return {
                    "success": True,
                    "confirmed": True,
                    "session_id": session.id,
                    "user_id": session.user_id,
                    "amount": confirmation_result.get("amount")
                }
            
            return {"success": True, "confirmed": False}
            
        except Exception as e:
            logger.error(f"Error checking payment confirmation: {e}")
            return {"success": False, "error": str(e)}
    
    async def _analyze_payment_sms(
        self,
        sms_content: str,
        payment_sessions: List[PaymentSession]
    ) -> Dict[str, Any]:
        """Analyze SMS content for payment confirmation"""
        try:
            import re
            
            # Common payment confirmation patterns
            patterns = [
                r'поступил.*?(\d+(?:\.\d{2})?)\s*сум',  # "поступил 123000 сум"
                r'зачислен.*?(\d+(?:\.\d{2})?)\s*сум',  # "зачислен 123000 сум"
                r'получен.*?(\d+(?:\.\d{2})?)\s*сум',   # "получен 123000 сум"
                r'перевод.*?(\d+(?:\.\d{2})?)\s*сум',   # "перевод 123000 сум"
                r'(\d+(?:\.\d{2})?)\s*сум.*?поступил',  # "123000 сум поступил"
                r'(\d+(?:\.\d{2})?)\s*сум.*?зачислен',  # "123000 сум зачислен"
            ]
            
            # Extract amount from SMS
            amount = None
            for pattern in patterns:
                match = re.search(pattern, sms_content.lower())
                if match:
                    amount = float(match.group(1).replace(',', ''))
                    break
            
            if amount is None:
                return {"confirmed": False, "reason": "No amount found in SMS"}
            
            # Find matching payment session
            for session in payment_sessions:
                # Allow 1% tolerance for amount matching
                tolerance = session.amount_uzs * 0.01
                if abs(amount - session.amount_uzs) <= tolerance:
                    return {
                        "confirmed": True,
                        "session": session,
                        "amount": amount,
                        "reason": f"Amount {amount} matches session {session.id}"
                    }
            
            return {
                "confirmed": False,
                "reason": f"Amount {amount} doesn't match any pending payment session"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing payment SMS: {e}")
            return {"confirmed": False, "reason": f"Analysis error: {str(e)}"}
    
    async def get_gsm_modules(self, db: AsyncSession) -> List[GSMModule]:
        """Get all GSM modules"""
        try:
            result = await db.execute(
                select(GSMModule).order_by(GSMModule.priority.desc(), GSMModule.created_at)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting GSM modules: {e}")
            return []
    
    async def create_gsm_module(
        self,
        db: AsyncSession,
        phone_number: str,
        bank_card_number: str,
        bank_name: str,
        card_holder_name: str,
        device_id: Optional[str] = None,
        description: Optional[str] = None,
        priority: int = 1
    ) -> GSMModule:
        """Create new GSM module"""
        try:
            gsm_module = GSMModule(
                phone_number=phone_number,
                bank_card_number=bank_card_number,
                bank_name=bank_name,
                card_holder_name=card_holder_name,
                device_id=device_id,
                description=description,
                priority=priority
            )
            
            db.add(gsm_module)
            await db.commit()
            await db.refresh(gsm_module)
            
            logger.info(f"Created GSM module {gsm_module.id}: {phone_number}")
            return gsm_module
            
        except Exception as e:
            logger.error(f"Error creating GSM module: {e}")
            await db.rollback()
            raise
    
    async def update_gsm_module(
        self,
        db: AsyncSession,
        module_id: int,
        **updates
    ) -> Optional[GSMModule]:
        """Update GSM module"""
        try:
            result = await db.execute(
                select(GSMModule).where(GSMModule.id == module_id)
            )
            gsm_module = result.scalar_one_or_none()
            
            if not gsm_module:
                return None
            
            for key, value in updates.items():
                if hasattr(gsm_module, key):
                    setattr(gsm_module, key, value)
            
            gsm_module.updated_at = datetime.utcnow()
            await db.commit()
            
            logger.info(f"Updated GSM module {module_id}")
            return gsm_module
            
        except Exception as e:
            logger.error(f"Error updating GSM module {module_id}: {e}")
            await db.rollback()
            raise
    
    async def delete_gsm_module(self, db: AsyncSession, module_id: int) -> bool:
        """Delete GSM module"""
        try:
            result = await db.execute(
                select(GSMModule).where(GSMModule.id == module_id)
            )
            gsm_module = result.scalar_one_or_none()
            
            if not gsm_module:
                return False
            
            await db.delete(gsm_module)
            await db.commit()
            
            logger.info(f"Deleted GSM module {module_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting GSM module {module_id}: {e}")
            await db.rollback()
            raise