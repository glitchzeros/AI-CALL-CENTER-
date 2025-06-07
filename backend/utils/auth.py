"""
Authentication utilities for admin access
"""

from jose import jwt
import logging
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("aetherium.auth")


async def get_current_admin_user(token: str, db: AsyncSession):
    """
    Verify admin user authentication and return admin user info
    """
    try:
        # Decode JWT token
        payload = jwt.decode(token, "your_secret_key", algorithms=["HS256"])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
        
        # Check if user exists and is admin
        query = """
            SELECT u.*, au.admin_level, au.permissions
            FROM users u
            JOIN admin_users au ON u.id = au.user_id
            WHERE u.id = $1 AND u.is_active = true
        """
        
        result = await db.execute(query, (user_id,))
        admin_record = result.fetchone()
        
        if not admin_record:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        return {
            "id": admin_record.id,
            "email": admin_record.email,
            "admin_level": admin_record.admin_level,
            "permissions": admin_record.permissions
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


def create_admin_token(user_id: str, admin_level: str) -> str:
    """Create JWT token for admin user"""
    payload = {
        "sub": user_id,
        "admin_level": admin_level,
        "exp": datetime.utcnow() + timedelta(hours=24),
        "iat": datetime.utcnow()
    }
    
    return jwt.encode(payload, "your_secret_key", algorithm="HS256")


def check_admin_permission(admin_user: dict, required_permission: str) -> bool:
    """Check if admin user has required permission"""
    if admin_user.get("admin_level") == "super_admin":
        return True
    
    permissions = admin_user.get("permissions", {})
    return permissions.get(required_permission, False) or permissions.get("all", False)