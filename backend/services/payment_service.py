"""
Payment service
The Scribe's Financial Guardian
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from database.connection import AsyncSessionLocal
from models.payment import PaymentTransaction
from models.user import User, UserSubscription, SubscriptionTier
from utils.security import generate_md5_signature

logger = logging.getLogger("aetherium.payments")

class PaymentService:
    """Service for handling Click API payments"""
    
    def __init__(self):
        self.secret_key = os.getenv("CLICK_SECRET_KEY", "")
        self.service_id = os.getenv("CLICK_SERVICE_ID", "")
        logger.info("💳 Payment service initialized")
    
    async def initiate_payment(
        self,
        user_id: int,
        tier_id: int,
        amount: float
    ) -> Dict[str, Any]:
        """
        Initiate payment process with Click API
        
        Args:
            user_id: User ID
            tier_id: Subscription tier ID
            amount: Payment amount in USD
            
        Returns:
            Payment initiation result
        """
        try:
            async with AsyncSessionLocal() as db:
                # Get user and tier info
                user_result = await db.execute(select(User).where(User.id == user_id))
                user = user_result.scalar_one_or_none()
                
                tier_result = await db.execute(select(SubscriptionTier).where(SubscriptionTier.id == tier_id))
                tier = tier_result.scalar_one_or_none()
                
                if not user or not tier:
                    raise ValueError("User or tier not found")
                
                # Create merchant transaction ID
                merchant_trans_id = f"aetherium_{user_id}_{tier_id}_{int(datetime.utcnow().timestamp())}"
                
                # Create payment transaction record
                payment = PaymentTransaction(
                    user_id=user_id,
                    merchant_trans_id=merchant_trans_id,
                    amount=amount,
                    status="pending"
                )
                
                db.add(payment)
                await db.commit()
                await db.refresh(payment)
                
                logger.info(f"Payment initiated: user={user_id}, amount=${amount}, merchant_id={merchant_trans_id}")
                
                # Return payment URL or redirect info
                # In a real implementation, this would redirect to Click payment page
                return {
                    "payment_id": payment.id,
                    "merchant_trans_id": merchant_trans_id,
                    "amount": amount,
                    "currency": "USD",
                    "redirect_url": f"https://my.click.uz/services/pay?service_id={self.service_id}&merchant_trans_id={merchant_trans_id}&amount={amount}",
                    "success": True
                }
                
        except Exception as e:
            logger.error(f"Payment initiation error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def process_click_callback(
        self,
        click_trans_id: int,
        service_id: int,
        click_paydoc_id: int,
        merchant_trans_id: str,
        amount: float,
        action: int,
        error: int,
        error_note: str,
        sign_time: str,
        sign_string: str
    ) -> Dict[str, Any]:
        """
        Process Click API callback
        
        Args:
            click_trans_id: Click transaction ID
            service_id: Service ID
            click_paydoc_id: Click payment document ID
            merchant_trans_id: Merchant transaction ID
            amount: Payment amount
            action: Action type (0=prepare, 1=complete)
            error: Error code (0=success)
            error_note: Error description
            sign_time: Signature timestamp
            sign_string: Security signature
            
        Returns:
            Callback processing result
        """
        try:
            async with AsyncSessionLocal() as db:
                # Find payment transaction
                payment_result = await db.execute(
                    select(PaymentTransaction).where(
                        PaymentTransaction.merchant_trans_id == merchant_trans_id
                    )
                )
                payment = payment_result.scalar_one_or_none()
                
                if not payment:
                    logger.error(f"Payment not found: {merchant_trans_id}")
                    return {"error": -1, "error_note": "Payment not found"}
                
                # Verify signature
                if not self._verify_signature(
                    click_trans_id, service_id, merchant_trans_id, 
                    amount, action, sign_time, sign_string, 
                    getattr(payment, 'merchant_prepare_id', None)
                ):
                    logger.error(f"Invalid signature for payment: {merchant_trans_id}")
                    return {"error": -1, "error_note": "Invalid signature"}
                
                if action == 0:  # Prepare
                    return await self._handle_prepare(
                        db, payment, click_trans_id, click_paydoc_id, amount, error, error_note, sign_time
                    )
                elif action == 1:  # Complete
                    return await self._handle_complete(
                        db, payment, click_trans_id, amount, error, error_note, sign_time
                    )
                else:
                    logger.error(f"Unknown action: {action}")
                    return {"error": -1, "error_note": "Unknown action"}
                    
        except Exception as e:
            logger.error(f"Callback processing error: {e}")
            return {"error": -1, "error_note": "Internal error"}
    
    async def _handle_prepare(
        self,
        db: AsyncSession,
        payment: PaymentTransaction,
        click_trans_id: int,
        click_paydoc_id: int,
        amount: float,
        error: int,
        error_note: str,
        sign_time: str
    ) -> Dict[str, Any]:
        """Handle prepare phase of payment"""
        
        # Update payment record
        payment.click_trans_id = click_trans_id
        payment.click_paydoc_id = click_paydoc_id
        payment.error_code = error
        payment.error_note = error_note
        payment.sign_time = datetime.fromisoformat(sign_time.replace(' ', 'T'))
        
        if error == 0:
            # Payment is valid, generate prepare ID
            payment.merchant_prepare_id = payment.id
            payment.status = "prepared"
            
            await db.commit()
            
            logger.info(f"Payment prepared: {payment.merchant_trans_id}")
            
            return {
                "click_trans_id": click_trans_id,
                "merchant_trans_id": payment.merchant_trans_id,
                "merchant_prepare_id": payment.merchant_prepare_id,
                "error": 0,
                "error_note": "Success"
            }
        else:
            # Payment preparation failed
            payment.status = "failed"
            await db.commit()
            
            logger.error(f"Payment preparation failed: {payment.merchant_trans_id}, error: {error}")
            
            return {
                "click_trans_id": click_trans_id,
                "merchant_trans_id": payment.merchant_trans_id,
                "error": error,
                "error_note": error_note
            }
    
    async def _handle_complete(
        self,
        db: AsyncSession,
        payment: PaymentTransaction,
        click_trans_id: int,
        amount: float,
        error: int,
        error_note: str,
        sign_time: str
    ) -> Dict[str, Any]:
        """Handle complete phase of payment"""
        
        payment.error_code = error
        payment.error_note = error_note
        payment.sign_time = datetime.fromisoformat(sign_time.replace(' ', 'T'))
        
        if error == 0:
            # Payment successful - activate subscription
            payment.status = "completed"
            
            # Get user and create/update subscription
            user_result = await db.execute(select(User).where(User.id == payment.user_id))
            user = user_result.scalar_one_or_none()
            
            if user:
                # Find tier from payment amount
                tier_result = await db.execute(
                    select(SubscriptionTier).where(SubscriptionTier.price_usd == amount)
                )
                tier = tier_result.scalar_one_or_none()
                
                if tier:
                    # Create new subscription
                    subscription = UserSubscription(
                        user_id=user.id,
                        tier_id=tier.id,
                        status="active",
                        started_at=datetime.utcnow(),
                        expires_at=datetime.utcnow() + timedelta(days=30),  # 30-day subscription
                        click_trans_id=click_trans_id,
                        click_merchant_trans_id=payment.merchant_trans_id
                    )
                    
                    db.add(subscription)
                    payment.subscription_id = subscription.id
                    
                    await db.commit()
                    
                    logger.info(f"Subscription activated: user={user.id}, tier={tier.name}")
                    
            return {
                "click_trans_id": click_trans_id,
                "merchant_trans_id": payment.merchant_trans_id,
                "merchant_confirm_id": payment.id,
                "error": 0,
                "error_note": "Success"
            }
        else:
            # Payment failed
            payment.status = "failed"
            await db.commit()
            
            logger.error(f"Payment completion failed: {payment.merchant_trans_id}, error: {error}")
            
            return {
                "click_trans_id": click_trans_id,
                "merchant_trans_id": payment.merchant_trans_id,
                "error": error,
                "error_note": error_note
            }
    
    def _verify_signature(
        self,
        click_trans_id: int,
        service_id: int,
        merchant_trans_id: str,
        amount: float,
        action: int,
        sign_time: str,
        sign_string: str,
        merchant_prepare_id: Optional[int] = None
    ) -> bool:
        """Verify Click API signature"""
        
        if action == 0:  # Prepare
            data_string = f"{click_trans_id}{service_id}{self.secret_key}{merchant_trans_id}{amount}{action}{sign_time}"
        else:  # Complete
            data_string = f"{click_trans_id}{service_id}{self.secret_key}{merchant_trans_id}{merchant_prepare_id or ''}{amount}{action}{sign_time}"
        
        expected_signature = generate_md5_signature(data_string)
        
        return expected_signature.lower() == sign_string.lower()