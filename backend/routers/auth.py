"""
Authentication router
The Scribe's Identity Verification
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging
import secrets
import hashlib
from datetime import datetime, timedelta

from database.connection import get_database
from models.user import User
from models.company_number import CompanyNumberPool
from services.sms_service import SMSService
from services.auth_service import AuthService
from utils.security import verify_password, hash_password, create_access_token

logger = logging.getLogger(__name__)
router = APIRouter()
security = HTTPBearer()

# Pydantic models
class UserRegistration(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    phone_number: str

class SMSVerification(BaseModel):
    email: str
    verification_code: str

class UserLogin(BaseModel):
    login_identifier: str  # Email or phone number
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: str
    company_number: Optional[str]
    is_first_login: bool

@router.post("/register", response_model=dict)
async def register_user(
    user_data: UserRegistration,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_database)
):
    """
    User registration with SMS verification
    The Scribe's New Client Enrollment
    """
    try:
        # Validate password confirmation
        if user_data.password != user_data.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        
        # Check if user already exists
        existing_user = await db.execute(
            select(User).where(
                (User.email == user_data.email) | 
                (User.phone_number == user_data.phone_number)
            )
        )
        if existing_user.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="User already exists with this email or phone number")
        
        # Generate SMS verification code
        verification_code = f"{secrets.randbelow(900000) + 100000:06d}"
        
        # Hash password
        password_hash = hash_password(user_data.password)
        
        # Create user
        new_user = User(
            email=user_data.email,
            phone_number=user_data.phone_number,
            password_hash=password_hash,
            sms_verification_code=verification_code,
            sms_verification_expires_at=datetime.utcnow() + timedelta(minutes=10)
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # Send SMS verification code
        sms_service = SMSService()
        background_tasks.add_task(
            sms_service.send_verification_sms,
            user_data.phone_number,
            verification_code
        )
        
        logger.info(f"User registered: {user_data.email}")
        
        return {
            "message": "Registration successful. Please verify your phone number with the SMS code.",
            "user_id": new_user.id,
            "verification_required": True
        }
        
    except Exception as e:
        logger.error(f"Registration error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Registration failed")

@router.post("/verify-sms", response_model=TokenResponse)
async def verify_sms_code(
    verification_data: SMSVerification,
    db: AsyncSession = Depends(get_database)
):
    """
    Verify SMS code and complete registration
    The Scribe's Identity Confirmation
    """
    try:
        # Find user by email
        result = await db.execute(
            select(User).where(User.email == verification_data.email)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check verification code
        if (user.sms_verification_code != verification_data.verification_code or
            user.sms_verification_expires_at < datetime.utcnow()):
            raise HTTPException(status_code=400, detail="Invalid or expired verification code")
        
        # Assign company number
        company_number_result = await db.execute(
            select(CompanyNumberPool).where(CompanyNumberPool.is_assigned == False).limit(1)
        )
        company_number_record = company_number_result.scalar_one_or_none()
        
        if not company_number_record:
            raise HTTPException(status_code=500, detail="No available company numbers")
        
        # Update user and company number
        user.is_verified = True
        user.company_number = company_number_record.phone_number
        user.sms_verification_code = None
        user.sms_verification_expires_at = None
        
        company_number_record.is_assigned = True
        company_number_record.assigned_user_id = user.id
        company_number_record.assigned_at = datetime.utcnow()
        
        await db.commit()
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        logger.info(f"User verified and company number assigned: {user.email} -> {user.company_number}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            email=user.email,
            company_number=user.company_number,
            is_first_login=True  # This is the first successful verification
        )
        
    except Exception as e:
        logger.error(f"SMS verification error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Verification failed")

@router.post("/login", response_model=TokenResponse)
async def login_user(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_database)
):
    """
    User login
    The Scribe's Client Authentication
    """
    try:
        # Find user by email or phone number
        result = await db.execute(
            select(User).where(
                (User.email == login_data.login_identifier) |
                (User.phone_number == login_data.login_identifier)
            )
        )
        user = result.scalar_one_or_none()
        
        if not user or not verify_password(login_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if not user.is_verified:
            raise HTTPException(status_code=401, detail="Account not verified")
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user.id)})
        
        logger.info(f"User logged in: {user.email}")
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user_id=user.id,
            email=user.email,
            company_number=user.company_number,
            is_first_login=False  # This is a subsequent login
        )
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

@router.post("/resend-sms")
async def resend_sms_code(
    email: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_database)
):
    """
    Resend SMS verification code
    The Scribe's Second Chance
    """
    try:
        # Find user
        result = await db.execute(
            select(User).where(User.email == email)
        )
        user = result.scalar_one_or_none()
        
        if not user or user.is_verified:
            raise HTTPException(status_code=400, detail="Invalid request")
        
        # Generate new code
        verification_code = f"{secrets.randbelow(900000) + 100000:06d}"
        
        # Update user
        user.sms_verification_code = verification_code
        user.sms_verification_expires_at = datetime.utcnow() + timedelta(minutes=10)
        
        await db.commit()
        
        # Send SMS
        sms_service = SMSService()
        background_tasks.add_task(
            sms_service.send_verification_sms,
            user.phone_number,
            verification_code
        )
        
        return {"message": "Verification code resent"}
        
    except Exception as e:
        logger.error(f"Resend SMS error: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to resend code")

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_database)
) -> User:
    """
    Get current authenticated user
    The Scribe's Identity Verification
    """
    try:
        auth_service = AuthService()
        user_id = auth_service.verify_token(credentials.credentials)
        
        result = await db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
        
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(status_code=401, detail="Invalid authentication")