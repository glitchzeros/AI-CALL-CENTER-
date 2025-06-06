"""
Authentication service
The Scribe's Identity Guardian
"""

import logging
from typing import Optional
from utils.security import verify_token

logger = logging.getLogger(__name__)

class AuthService:
    """Service for handling authentication operations"""
    
    def __init__(self):
        logger.info("🔐 Auth service initialized")
    
    def verify_token(self, token: str) -> int:
        """
        Verify JWT token and return user ID
        
        Args:
            token: JWT token string
            
        Returns:
            User ID if token is valid
            
        Raises:
            ValueError: If token is invalid
        """
        return verify_token(token)
    
    def is_token_valid(self, token: str) -> bool:
        """
        Check if token is valid without raising exceptions
        
        Args:
            token: JWT token string
            
        Returns:
            True if token is valid, False otherwise
        """
        try:
            self.verify_token(token)
            return True
        except ValueError:
            return False