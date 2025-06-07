"""
Custom exceptions for Aetherium
The Scribe's Error Codex
"""

from fastapi import HTTPException
from typing import Any, Dict, Optional


class AetheriumException(Exception):
    """Base exception for Aetherium application"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(AetheriumException):
    """Raised when data validation fails"""
    def __init__(self, message: str = "Validation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class NotFoundError(AetheriumException):
    """Raised when a requested resource is not found"""
    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class ConflictError(AetheriumException):
    """Raised when there's a conflict with existing data"""
    def __init__(self, message: str = "Resource conflict", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class AuthenticationError(AetheriumException):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class AuthorizationError(AetheriumException):
    """Raised when authorization fails"""
    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class DatabaseError(AetheriumException):
    """Raised when database operations fail"""
    def __init__(self, message: str = "Database operation failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class ExternalServiceError(AetheriumException):
    """Raised when external service calls fail"""
    def __init__(self, message: str = "External service error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class ConfigurationError(AetheriumException):
    """Raised when configuration is invalid"""
    def __init__(self, message: str = "Configuration error", details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


# HTTP Exception helpers
def to_http_exception(exc: AetheriumException) -> HTTPException:
    """Convert Aetherium exception to FastAPI HTTPException"""
    if isinstance(exc, ValidationError):
        return HTTPException(status_code=400, detail={"message": exc.message, "details": exc.details})
    elif isinstance(exc, NotFoundError):
        return HTTPException(status_code=404, detail={"message": exc.message, "details": exc.details})
    elif isinstance(exc, ConflictError):
        return HTTPException(status_code=409, detail={"message": exc.message, "details": exc.details})
    elif isinstance(exc, AuthenticationError):
        return HTTPException(status_code=401, detail={"message": exc.message, "details": exc.details})
    elif isinstance(exc, AuthorizationError):
        return HTTPException(status_code=403, detail={"message": exc.message, "details": exc.details})
    else:
        return HTTPException(status_code=500, detail={"message": exc.message, "details": exc.details})