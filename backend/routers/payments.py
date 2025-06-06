"""
Payments router
The Scribe's Financial Interface
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import List, Optional

from database.connection import get_database
from models.user import User
from models.payment import PaymentTransaction
from routers.auth import get_current_user

router = APIRouter()

class PaymentTransactionResponse(BaseModel):
    id: int
    click_trans_id: Optional[int]
    merchant_trans_id: Optional[str]
    amount: float
    status: str
    error_code: Optional[int]
    error_note: Optional[str]
    created_at: str
    updated_at: str

@router.get("/transactions", response_model=List[PaymentTransactionResponse])
async def get_payment_transactions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database),
    limit: int = 20,
    offset: int = 0
):
    """
    Get user's payment transactions
    The Scribe's Financial History
    """
    try:
        result = await db.execute(
            select(PaymentTransaction).where(
                PaymentTransaction.user_id == current_user.id
            ).order_by(desc(PaymentTransaction.created_at)).limit(limit).offset(offset)
        )
        
        transactions = result.scalars().all()
        
        return [
            PaymentTransactionResponse(
                id=transaction.id,
                click_trans_id=transaction.click_trans_id,
                merchant_trans_id=transaction.merchant_trans_id,
                amount=float(transaction.amount),
                status=transaction.status,
                error_code=transaction.error_code,
                error_note=transaction.error_note,
                created_at=transaction.created_at.isoformat(),
                updated_at=transaction.updated_at.isoformat()
            )
            for transaction in transactions
        ]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get payment transactions")

@router.get("/transactions/{transaction_id}", response_model=PaymentTransactionResponse)
async def get_payment_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Get specific payment transaction
    The Scribe's Financial Record
    """
    try:
        result = await db.execute(
            select(PaymentTransaction).where(
                PaymentTransaction.id == transaction_id,
                PaymentTransaction.user_id == current_user.id
            )
        )
        
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Payment transaction not found")
        
        return PaymentTransactionResponse(
            id=transaction.id,
            click_trans_id=transaction.click_trans_id,
            merchant_trans_id=transaction.merchant_trans_id,
            amount=float(transaction.amount),
            status=transaction.status,
            error_code=transaction.error_code,
            error_note=transaction.error_note,
            created_at=transaction.created_at.isoformat(),
            updated_at=transaction.updated_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get payment transaction")

@router.get("/status/{merchant_trans_id}")
async def get_payment_status(
    merchant_trans_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Get payment status by merchant transaction ID
    The Scribe's Payment Inquiry
    """
    try:
        result = await db.execute(
            select(PaymentTransaction).where(
                PaymentTransaction.merchant_trans_id == merchant_trans_id,
                PaymentTransaction.user_id == current_user.id
            )
        )
        
        transaction = result.scalar_one_or_none()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        return {
            "merchant_trans_id": merchant_trans_id,
            "status": transaction.status,
            "amount": float(transaction.amount),
            "click_trans_id": transaction.click_trans_id,
            "error_code": transaction.error_code,
            "error_note": transaction.error_note,
            "created_at": transaction.created_at.isoformat(),
            "updated_at": transaction.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to get payment status")