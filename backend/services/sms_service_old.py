"""
SMS service
The Scribe's Message Courier
"""

import logging
import asyncio
import httpx
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.connection import get_database
from models.modem import GSMModem

logger = logging.getLogger(__name__)

class SMSService:
    """Service for sending SMS messages"""
    
    def __init__(self):
        self.modem_manager_url = "http://modem-manager:8001"
        logger.info("📱 SMS service initialized")
    
    async def is_demo_mode_available(self) -> bool:
        """Check if demo mode should be used (no GSM modules available)"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.modem_manager_url}/status",
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    status = response.json()
                    available_modems = status.get("available_modems", 0)
                    return available_modems == 0
                else:
                    # If modem manager is not available, use demo mode
                    return True
                    
        except Exception as e:
            logger.warning(f"Cannot check modem status, using demo mode: {e}")
            return True
    
    async def send_login_verification_sms(self, phone_number: str, verification_code: str) -> bool:
        """
        Send SMS verification code for login
        
        Args:
            phone_number: Recipient phone number
            verification_code: 6-digit verification code
            
        Returns:
            True if SMS was sent successfully
        """
        try:
            message = f"Ваш код входа в Aetherium: {verification_code}. Код действителен 10 минут."
            
            # Send via modem manager
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.modem_manager_url}/send-sms",
                    json={
                        "to_number": phone_number,
                        "content": message,
                        "priority": "high"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    logger.info(f"Login verification SMS sent to {phone_number}")
                    return True
                else:
                    logger.error(f"Failed to send login SMS: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Login SMS sending error: {e}")
            return False
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.modem_manager_url}/status",
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    status = response.json()
                    real_modems = status.get("real_modems_count", 0)
                    return real_modems == 0
                else:
                    # If modem manager is not available, use demo mode
                    return True
                    
        except Exception as e:
            logger.warning(f"Could not check modem manager status: {e}")
            return True  # Default to demo mode if can't connect
    
    async def send_verification_sms(self, phone_number: str, verification_code: str) -> bool:
        """
        Send SMS verification code
        
        Args:
            phone_number: Recipient phone number
            verification_code: 6-digit verification code
            
        Returns:
            True if SMS was sent successfully
        """
        try:
            message = f"Ваш код подтверждения Aetherium: {verification_code}. Код действителен 10 минут."
            
            # Send via modem manager
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.modem_manager_url}/send-sms",
                    json={
                        "to_number": phone_number,
                        "content": message,
                        "priority": "high"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    logger.info(f"Verification SMS sent to {phone_number}")
                    return True
                else:
                    logger.error(f"Failed to send SMS: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"SMS sending error: {e}")
            return False
    
    async def send_sms(
        self,
        to_number: str,
        content: str,
        from_number: Optional[str] = None,
        session_id: Optional[int] = None
    ) -> bool:
        """
        Send SMS message
        
        Args:
            to_number: Recipient phone number
            content: Message content
            from_number: Sender number (optional, will use available modem)
            session_id: Associated session ID (optional)
            
        Returns:
            True if SMS was sent successfully
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.modem_manager_url}/send-sms",
                    json={
                        "to_number": to_number,
                        "content": content,
                        "from_number": from_number,
                        "session_id": session_id
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    logger.info(f"SMS sent to {to_number}")
                    return True
                else:
                    logger.error(f"Failed to send SMS: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"SMS sending error: {e}")
            return False
    async def send_login_verification_sms(self, phone_number: str, verification_code: str) -> bool:
        """
        Send SMS verification code for login
        
        Args:
            phone_number: Recipient phone number
            verification_code: 6-digit verification code
            
        Returns:
            True if SMS was sent successfully
        """
        try:
            message = f"Ваш код входа в Aetherium: {verification_code}. Код действителен 10 минут."
            
            # Send via modem manager
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.modem_manager_url}/send-sms",
                    json={
                        "to_number": phone_number,
                        "content": message,
                        "priority": "high",
                        "sms_type": "login_verification"
                    },
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    logger.info(f"Login verification SMS sent to {phone_number}")
                    return True
                else:
                    logger.error(f"Failed to send login SMS: {response.status_code} - {response.text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Login SMS sending error: {e}")
            return False
