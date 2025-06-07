"""
Enhanced middleware for Aetherium Backend
"""

import time
import uuid
import logging
from typing import Callable, Optional
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import traceback

logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all requests and responses"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        
        # Log request
        start_time = time.time()
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "method": request.method,
                "url": str(request.url),
                "client_ip": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            }
        )
        
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log response
            logger.info(
                f"Request completed: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "process_time": process_time,
                }
            )
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "error": str(e),
                    "process_time": process_time,
                    "traceback": traceback.format_exc(),
                }
            )
            raise


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for handling and formatting errors"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            return await call_next(request)
        except HTTPException as e:
            # Handle FastAPI HTTP exceptions
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "success": False,
                    "error": e.detail,
                    "error_code": getattr(e, 'error_code', None),
                    "request_id": getattr(request.state, 'request_id', None),
                    "timestamp": time.time(),
                }
            )
        except ValueError as e:
            # Handle validation errors
            logger.error(f"Validation error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "error": "Invalid input data",
                    "details": str(e),
                    "request_id": getattr(request.state, 'request_id', None),
                    "timestamp": time.time(),
                }
            )
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={
                    "success": False,
                    "error": "Internal server error",
                    "request_id": getattr(request.state, 'request_id', None),
                    "timestamp": time.time(),
                }
            )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Add CORS headers for development
        if request.headers.get("origin"):
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Origin, X-Requested-With, Content-Type, Accept, Authorization, X-Request-ID"
            response.headers["Access-Control-Expose-Headers"] = "X-Request-ID, X-Process-Time"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware"""
    
    def __init__(self, app: ASGIApp, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts = {}
        self.last_reset = time.time()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Reset counts every minute
        current_time = time.time()
        if current_time - self.last_reset > 60:
            self.request_counts.clear()
            self.last_reset = current_time
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        current_count = self.request_counts.get(client_ip, 0)
        if current_count >= self.requests_per_minute:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "error": "Rate limit exceeded",
                    "retry_after": 60 - (current_time - self.last_reset),
                    "request_id": getattr(request.state, 'request_id', None),
                    "timestamp": current_time,
                }
            )
        
        # Increment count
        self.request_counts[client_ip] = current_count + 1
        
        return await call_next(request)


class DatabaseConnectionMiddleware(BaseHTTPMiddleware):
    """Middleware for managing database connections"""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            # Database connection will be handled by dependency injection
            response = await call_next(request)
            return response
        except Exception as e:
            # Log database-related errors
            if "database" in str(e).lower() or "connection" in str(e).lower():
                logger.error(f"Database error: {str(e)}", exc_info=True)
                return JSONResponse(
                    status_code=503,
                    content={
                        "success": False,
                        "error": "Database service temporarily unavailable",
                        "request_id": getattr(request.state, 'request_id', None),
                        "timestamp": time.time(),
                    }
                )
            raise


def create_custom_http_exception(
    status_code: int,
    message: str,
    error_code: Optional[str] = None,
    details: Optional[dict] = None
) -> HTTPException:
    """Create a custom HTTP exception with additional metadata"""
    exception = HTTPException(status_code=status_code, detail=message)
    exception.error_code = error_code
    exception.details = details
    return exception


# Custom exception classes
class ValidationException(HTTPException):
    """Custom exception for validation errors"""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[dict] = None):
        super().__init__(status_code=422, detail=message)
        self.field = field
        self.details = details
        self.error_code = "VALIDATION_ERROR"


class AuthenticationException(HTTPException):
    """Custom exception for authentication errors"""
    
    def __init__(self, message: str = "Authentication required"):
        super().__init__(status_code=401, detail=message)
        self.error_code = "AUTHENTICATION_ERROR"


class AuthorizationException(HTTPException):
    """Custom exception for authorization errors"""
    
    def __init__(self, message: str = "Access denied"):
        super().__init__(status_code=403, detail=message)
        self.error_code = "AUTHORIZATION_ERROR"


class ResourceNotFoundException(HTTPException):
    """Custom exception for resource not found errors"""
    
    def __init__(self, resource: str, identifier: str):
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(status_code=404, detail=message)
        self.error_code = "RESOURCE_NOT_FOUND"
        self.resource = resource
        self.identifier = identifier


class BusinessLogicException(HTTPException):
    """Custom exception for business logic errors"""
    
    def __init__(self, message: str, error_code: str = "BUSINESS_LOGIC_ERROR"):
        super().__init__(status_code=400, detail=message)
        self.error_code = error_code


class ExternalServiceException(HTTPException):
    """Custom exception for external service errors"""
    
    def __init__(self, service: str, message: str = None):
        default_message = f"External service '{service}' is temporarily unavailable"
        super().__init__(status_code=503, detail=message or default_message)
        self.error_code = "EXTERNAL_SERVICE_ERROR"
        self.service = service


# Utility functions for error handling
def handle_database_error(error: Exception) -> HTTPException:
    """Handle database-specific errors"""
    error_str = str(error).lower()
    
    if "unique constraint" in error_str or "duplicate" in error_str:
        return ValidationException("Resource already exists")
    elif "foreign key" in error_str:
        return ValidationException("Referenced resource does not exist")
    elif "not null" in error_str:
        return ValidationException("Required field is missing")
    elif "connection" in error_str:
        return ExternalServiceException("database", "Database connection failed")
    else:
        logger.error(f"Unhandled database error: {error}", exc_info=True)
        return HTTPException(status_code=500, detail="Database operation failed")


def handle_external_api_error(service: str, error: Exception) -> HTTPException:
    """Handle external API errors"""
    error_str = str(error).lower()
    
    if "timeout" in error_str:
        return ExternalServiceException(service, f"{service} service timeout")
    elif "connection" in error_str:
        return ExternalServiceException(service, f"Cannot connect to {service}")
    elif "unauthorized" in error_str or "401" in error_str:
        return ExternalServiceException(service, f"{service} authentication failed")
    elif "forbidden" in error_str or "403" in error_str:
        return ExternalServiceException(service, f"{service} access denied")
    elif "not found" in error_str or "404" in error_str:
        return ExternalServiceException(service, f"{service} resource not found")
    else:
        logger.error(f"Unhandled {service} API error: {error}", exc_info=True)
        return ExternalServiceException(service)


def validate_request_data(data: dict, required_fields: list, optional_fields: list = None) -> dict:
    """Validate request data and return cleaned data"""
    if optional_fields is None:
        optional_fields = []
    
    errors = {}
    cleaned_data = {}
    
    # Check required fields
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            errors[field] = f"{field} is required"
        else:
            cleaned_data[field] = data[field]
    
    # Add optional fields if present
    for field in optional_fields:
        if field in data and data[field] is not None:
            cleaned_data[field] = data[field]
    
    # Check for unexpected fields
    allowed_fields = set(required_fields + optional_fields)
    unexpected_fields = set(data.keys()) - allowed_fields
    if unexpected_fields:
        errors["_unexpected"] = f"Unexpected fields: {', '.join(unexpected_fields)}"
    
    if errors:
        raise ValidationException(
            "Validation failed",
            details={"field_errors": errors}
        )
    
    return cleaned_data