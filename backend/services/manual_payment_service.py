"""
Manual Payment Service
Handles bank transfer payments with SMS confirmation via GSM modules
"""

import os
import logging
import time
import uuid
import re
from typing import Dict, Optional, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass
import asyncio

logger = logging.getLogger("aetherium.manual_payments")

@dataclass
class PaymentSession:
    payment_id: str
    user_id: int
    tier_name: str
    amount_uzs: float
    reference_code: str
    company_number: str
    created_at: datetime
    expires_at: datetime
    status: str = "pending"  # pending, confirmed, expired, cancelled

class ManualPaymentService:
    """Service for handling manual bank transfer payments with SMS confirmation"""
    
    def __init__(self):
        self.company_bank_card = os.getenv("COMPANY_BANK_CARD")
        self.company_bank_name = os.getenv("COMPANY_BANK_NAME", "Xalq Banki")
        self.company_cardholder_name = os.getenv("COMPANY_CARDHOLDER_NAME", "Aetherium LLC")
        self.company_bank_phone = os.getenv("COMPANY_BANK_PHONE", "+998901234567")
        
        # Payment window duration (30 minutes)
        self.payment_window_minutes = 30
        
        # Active payment sessions
        self.active_sessions: Dict[str, PaymentSession] = {}
        
        # USD to UZS exchange rate (should be updated regularly)
        self.usd_to_uzs_rate = 12300  # Approximate rate, should be dynamic
        
        if not self.company_bank_card:
            logger.warning("Company bank card not configured")
    
    def _generate_reference_code(self, user_id: int, tier_name: str) -> str:
        """Generate unique reference code for payment"""
        timestamp = int(time.time())
        return f"AET{user_id:06d}{timestamp % 10000:04d}"
    
    def _usd_to_uzs(self, usd_amount: float) -> float:
        """Convert USD to UZS"""
        return round(usd_amount * self.usd_to_uzs_rate, 0)
    
    async def initiate_consultation_payment(self, user_id: int, tier_name: str, 
                                          tier_price_usd: float, company_number: str) -> Dict[str, Any]:
        """Initiate payment after AI consultation"""
        try:
            # Convert USD to UZS
            amount_uzs = self._usd_to_uzs(tier_price_usd)
            
            # Generate unique reference code
            reference_code = self._generate_reference_code(user_id, tier_name)
            
            # Create payment session
            payment_id = f"manual_{int(time.time())}_{user_id}"
            session = PaymentSession(
                payment_id=payment_id,
                user_id=user_id,
                tier_name=tier_name,
                amount_uzs=amount_uzs,
                reference_code=reference_code,
                company_number=company_number,
                created_at=datetime.utcnow(),
                expires_at=datetime.utcnow() + timedelta(minutes=self.payment_window_minutes)
            )
            
            # Store active session
            self.active_sessions[payment_id] = session
            
            # Generate payment instructions
            instructions = self._generate_payment_instructions(session, tier_price_usd)
            
            logger.info(f"Payment session created: {payment_id} for user {user_id}")
            
            return {
                "success": True,
                "payment_id": payment_id,
                "reference_code": reference_code,
                "amount_uzs": amount_uzs,
                "amount_usd": tier_price_usd,
                "expires_at": session.expires_at.isoformat(),
                "remaining_minutes": self.payment_window_minutes,
                "payment_instructions": instructions,
                "bank_details": {
                    "card_number": self.company_bank_card,
                    "bank_name": self.company_bank_name,
                    "cardholder_name": self.company_cardholder_name,
                    "currency": "UZS"
                }
            }
            
        except Exception as e:
            logger.error(f"Error initiating consultation payment: {e}")
            return {
                "success": False,
                "error": "Payment initiation failed"
            }
    
    def _generate_payment_instructions(self, session: PaymentSession, usd_amount: float) -> Dict[str, Any]:
        """Generate detailed payment instructions"""
        return {
            "title": f"To'lov ko'rsatmalari - {session.tier_name} obuna",
            "amount_display": f"{session.amount_uzs:,.0f} so'm (${usd_amount:.2f})",
            "reference_code": session.reference_code,
            "instructions": [
                f"Karta raqami: {self.company_bank_card}",
                f"Bank: {self.company_bank_name}",
                f"Karta egasi: {self.company_cardholder_name}",
                f"Miqdor: {session.amount_uzs:,.0f} so'm",
                f"Izoh (majburiy): {session.reference_code}",
                "Vaqt chegarasi: 30 daqiqa"
            ],
            "important_notes": [
                "To'lov izohida albatta reference kodni ko'rsating",
                "Aynan belgilangan miqdorni o'tkazing",
                "30 daqiqa ichida to'lovni amalga oshiring",
                "SMS tasdiq kompaniya raqamiga keladi",
                "Obuna avtomatik faollashadi"
            ],
            "warning": "Diqqat: To'lov ma'lumotlari 30 daqiqa davomida ko'rinadi!"
        }
    
    async def check_payment_status(self, payment_id: str) -> Dict[str, Any]:
        """Check payment session status"""
        try:
            session = self.active_sessions.get(payment_id)
            if not session:
                return {
                    "success": False,
                    "error": "Payment session not found"
                }
            
            now = datetime.utcnow()
            
            # Check if expired
            if now > session.expires_at and session.status == "pending":
                session.status = "expired"
                logger.info(f"Payment session expired: {payment_id}")
            
            remaining_seconds = max(0, (session.expires_at - now).total_seconds())
            remaining_minutes = remaining_seconds / 60
            
            return {
                "success": True,
                "payment_id": payment_id,
                "status": session.status,
                "remaining_minutes": remaining_minutes,
                "is_expired": session.status == "expired",
                "reference_code": session.reference_code,
                "amount_uzs": session.amount_uzs
            }
            
        except Exception as e:
            logger.error(f"Error checking payment status: {e}")
            return {
                "success": False,
                "error": "Failed to check payment status"
            }
    
    async def process_sms_confirmation(self, sms_content: str, sender_number: str, 
                                     received_at: datetime = None) -> Dict[str, Any]:
        """Process incoming SMS for payment confirmation"""
        try:
            if received_at is None:
                received_at = datetime.utcnow()
            
            logger.info(f"Processing SMS from {sender_number}: {sms_content[:100]}...")
            
            # Analyze SMS content
            analysis = await self._analyze_payment_sms(sms_content)
            
            if not analysis["is_payment_confirmation"]:
                return {
                    "success": True,
                    "confirmed": False,
                    "reason": "SMS is not a payment confirmation"
                }
            
            # Find matching payment session
            matching_session = await self._find_matching_session(analysis)
            
            if not matching_session:
                logger.warning(f"No matching session found for SMS: {analysis}")
                return {
                    "success": True,
                    "confirmed": False,
                    "reason": "No matching payment session found"
                }
            
            # Confirm payment
            matching_session.status = "confirmed"
            
            logger.info(f"Payment confirmed for session {matching_session.payment_id}")
            
            return {
                "success": True,
                "confirmed": True,
                "payment_id": matching_session.payment_id,
                "user_id": matching_session.user_id,
                "tier_name": matching_session.tier_name,
                "amount_uzs": matching_session.amount_uzs,
                "reference_code": matching_session.reference_code,
                "confirmation_time": received_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing SMS confirmation: {e}")
            return {
                "success": False,
                "error": "Failed to process SMS confirmation"
            }
    
    async def _analyze_payment_sms(self, sms_content: str) -> Dict[str, Any]:
        """Analyze SMS content to detect payment confirmation"""
        try:
            content_lower = sms_content.lower()
            
            # Payment confirmation keywords in Uzbek and Russian
            confirmation_keywords = [
                # Uzbek
                "o'tkazma", "to'lov", "kredit", "hisobga", "qabul qilindi", 
                "muvaffaqiyatli", "tasdiqlandi", "amalga oshirildi",
                # Russian  
                "перевод", "платеж", "зачислен", "поступил", "успешно", 
                "подтвержден", "выполнен", "кредит",
                # English
                "transfer", "payment", "credited", "received", "successful", 
                "confirmed", "completed"
            ]
            
            # Check for confirmation keywords
            has_confirmation = any(keyword in content_lower for keyword in confirmation_keywords)
            
            # Extract amount (UZS patterns)
            amount_patterns = [
                r'(\d{1,3}(?:[,\s]\d{3})*(?:\.\d{2})?)\s*(?:so\'m|сум|uzs)',
                r'(\d{1,3}(?:[,\s]\d{3})*(?:\.\d{2})?)\s*(?:so\'m|сум)',
                r'(\d+(?:[,\s]\d{3})*(?:\.\d{2})?)'
            ]
            
            extracted_amount = None
            for pattern in amount_patterns:
                match = re.search(pattern, content_lower)
                if match:
                    amount_str = match.group(1).replace(',', '').replace(' ', '')
                    try:
                        extracted_amount = float(amount_str)
                        break
                    except ValueError:
                        continue
            
            # Extract reference code (AET format)
            reference_pattern = r'AET\d{10}'
            reference_match = re.search(reference_pattern, sms_content, re.IGNORECASE)
            extracted_reference = reference_match.group(0) if reference_match else None
            
            # Extract card number (last 4 digits)
            card_pattern = r'\*{4,}\d{4}'
            card_match = re.search(card_pattern, sms_content)
            extracted_card_digits = card_match.group(0)[-4:] if card_match else None
            
            # Determine if this is a payment confirmation
            is_confirmation = (
                has_confirmation and 
                (extracted_amount is not None or extracted_reference is not None)
            )
            
            return {
                "is_payment_confirmation": is_confirmation,
                "amount": extracted_amount,
                "reference_code": extracted_reference,
                "card_last_digits": extracted_card_digits,
                "keywords_found": has_confirmation,
                "confidence": 0.9 if is_confirmation else 0.1,
                "raw_content": sms_content
            }
            
        except Exception as e:
            logger.error(f"Error analyzing payment SMS: {e}")
            return {
                "is_payment_confirmation": False,
                "error": str(e)
            }
    
    async def _find_matching_session(self, analysis: Dict[str, Any]) -> Optional[PaymentSession]:
        """Find payment session matching SMS analysis"""
        try:
            reference_code = analysis.get("reference_code")
            amount = analysis.get("amount")
            
            # First try to match by reference code (most reliable)
            if reference_code:
                for session in self.active_sessions.values():
                    if (session.reference_code == reference_code and 
                        session.status == "pending"):
                        return session
            
            # If no reference match, try amount matching for recent sessions
            if amount:
                now = datetime.utcnow()
                for session in self.active_sessions.values():
                    if (session.status == "pending" and
                        abs(session.amount_uzs - amount) < 1000 and  # Allow 1000 UZS tolerance
                        (now - session.created_at).total_seconds() < 3600):  # Within 1 hour
                        return session
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding matching session: {e}")
            return None
    
    async def cleanup_expired_sessions(self):
        """Clean up expired payment sessions"""
        try:
            now = datetime.utcnow()
            expired_sessions = []
            
            for payment_id, session in self.active_sessions.items():
                if now > session.expires_at and session.status == "pending":
                    session.status = "expired"
                    expired_sessions.append(payment_id)
            
            # Remove expired sessions after 24 hours
            cutoff_time = now - timedelta(hours=24)
            for payment_id in list(self.active_sessions.keys()):
                session = self.active_sessions[payment_id]
                if session.created_at < cutoff_time:
                    del self.active_sessions[payment_id]
                    logger.info(f"Removed old session: {payment_id}")
            
            if expired_sessions:
                logger.info(f"Marked {len(expired_sessions)} sessions as expired")
                
        except Exception as e:
            logger.error(f"Error cleaning up sessions: {e}")
    
    def get_active_sessions_count(self) -> int:
        """Get count of active payment sessions"""
        return len([s for s in self.active_sessions.values() if s.status == "pending"])
    
    def get_session_by_user(self, user_id: int) -> Optional[PaymentSession]:
        """Get active payment session for user"""
        for session in self.active_sessions.values():
            if session.user_id == user_id and session.status == "pending":
                return session
        return None
    
    async def cancel_payment_session(self, payment_id: str) -> bool:
        """Cancel payment session"""
        try:
            session = self.active_sessions.get(payment_id)
            if session and session.status == "pending":
                session.status = "cancelled"
                logger.info(f"Payment session cancelled: {payment_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error cancelling session: {e}")
            return False
    
    def get_company_bank_info(self) -> Dict[str, str]:
        """Get company bank information"""
        return {
            "bank_card": self.company_bank_card,
            "bank_name": self.company_bank_name,
            "cardholder_name": self.company_cardholder_name,
            "bank_phone": self.company_bank_phone
        }