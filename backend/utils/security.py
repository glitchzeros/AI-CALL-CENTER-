"""
Security utilities
The Scribe's Protective Enchantments
"""

import os
from jose import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "aetherium_jwt_secret_2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

# Encryption for sensitive data (like bank card numbers)
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    ENCRYPTION_KEY = Fernet.generate_key()
elif isinstance(ENCRYPTION_KEY, str):
    # If it's a string, try to use it as base64, otherwise generate a new key
    try:
        ENCRYPTION_KEY = ENCRYPTION_KEY.encode()
        Fernet(ENCRYPTION_KEY)  # Test if it's valid
    except:
        ENCRYPTION_KEY = Fernet.generate_key()
        
cipher_suite = Fernet(ENCRYPTION_KEY)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> int:
    """Verify a JWT token and return user ID"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise ValueError("Invalid token payload")
        return int(user_id)
    except jwt.PyJWTError as e:
        logger.error(f"JWT verification error: {e}")
        raise ValueError("Invalid token")

def encrypt_sensitive_data(data: str) -> str:
    """Encrypt sensitive data like bank card numbers"""
    try:
        encrypted_data = cipher_suite.encrypt(data.encode())
        return encrypted_data.decode()
    except Exception as e:
        logger.error(f"Encryption error: {e}")
        raise

def decrypt_sensitive_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    try:
        decrypted_data = cipher_suite.decrypt(encrypted_data.encode())
        return decrypted_data.decode()
    except Exception as e:
        logger.error(f"Decryption error: {e}")
        raise

def generate_md5_signature(data_string: str) -> str:
    """Generate MD5 hash for Click API signatures"""
    import hashlib
    return hashlib.md5(data_string.encode()).hexdigest()