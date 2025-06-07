"""
Enhanced Logging Configuration
The Scribe's Chronicle System
"""

import logging
import logging.handlers
import os
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'session_id'):
            log_entry['session_id'] = record.session_id
        if hasattr(record, 'error_code'):
            log_entry['error_code'] = record.error_code
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging():
    """Setup comprehensive logging configuration for the Aetherium backend"""
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Determine log level from environment
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    numeric_level = getattr(logging, log_level, logging.INFO)
    
    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_formatter = ColoredFormatter(
        '%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    
    # Main application log file (JSON format for parsing)
    app_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / 'aetherium.log',
        maxBytes=20*1024*1024,  # 20MB
        backupCount=10,
        encoding='utf-8'
    )
    app_handler.setLevel(logging.INFO)
    app_handler.setFormatter(JSONFormatter())
    
    # Error log file (only errors and above)
    error_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / 'errors.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=10,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter())
    
    # Configure root logger
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(app_handler)
    root_logger.addHandler(error_handler)
    
    # Set specific log levels for different modules
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    # Create specialized loggers with dedicated files
    setup_specialized_loggers(log_dir)
    
    logging.info("📜 Aetherium enhanced logging system initialized")


def setup_specialized_loggers(log_dir: Path):
    """Setup specialized loggers for different components"""
    
    # Session logger for conversation tracking
    session_logger = logging.getLogger("aetherium.sessions")
    session_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / 'sessions.log',
        maxBytes=50*1024*1024,  # 50MB
        backupCount=15,
        encoding='utf-8'
    )
    session_handler.setFormatter(JSONFormatter())
    session_logger.addHandler(session_handler)
    session_logger.setLevel(logging.INFO)
    session_logger.propagate = False  # Don't propagate to root logger
    
    # Payment logger for financial transactions (critical for audit)
    payment_logger = logging.getLogger("aetherium.payments")
    payment_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / 'payments.log',
        maxBytes=20*1024*1024,  # 20MB
        backupCount=50,  # Keep more payment logs for audit
        encoding='utf-8'
    )
    payment_handler.setFormatter(JSONFormatter())
    payment_logger.addHandler(payment_handler)
    payment_logger.setLevel(logging.INFO)
    payment_logger.propagate = False
    
    # Security logger for authentication and authorization events
    security_logger = logging.getLogger("aetherium.security")
    security_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / 'security.log',
        maxBytes=30*1024*1024,  # 30MB
        backupCount=20,
        encoding='utf-8'
    )
    security_handler.setFormatter(JSONFormatter())
    security_logger.addHandler(security_handler)
    security_logger.setLevel(logging.INFO)
    security_logger.propagate = False
    
    # API access logger for monitoring and analytics
    api_logger = logging.getLogger("aetherium.api")
    api_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / 'api_access.log',
        maxBytes=40*1024*1024,  # 40MB
        backupCount=10,
        encoding='utf-8'
    )
    api_handler.setFormatter(JSONFormatter())
    api_logger.addHandler(api_handler)
    api_logger.setLevel(logging.INFO)
    api_logger.propagate = False
    
    # Dream journal logger for AI insights
    dream_logger = logging.getLogger("aetherium.dreams")
    dream_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / 'dream_journal.log',
        maxBytes=15*1024*1024,  # 15MB
        backupCount=10,
        encoding='utf-8'
    )
    dream_handler.setFormatter(JSONFormatter())
    dream_logger.addHandler(dream_handler)
    dream_logger.setLevel(logging.INFO)
    dream_logger.propagate = False
    
    # Modem communication logger
    modem_logger = logging.getLogger("aetherium.modems")
    modem_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / 'modems.log',
        maxBytes=30*1024*1024,  # 30MB
        backupCount=7,
        encoding='utf-8'
    )
    modem_handler.setFormatter(JSONFormatter())
    modem_logger.addHandler(modem_handler)
    modem_logger.setLevel(logging.INFO)
    modem_logger.propagate = False
    
    # Workflow execution logger
    workflow_logger = logging.getLogger("aetherium.workflows")
    workflow_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / 'workflows.log',
        maxBytes=25*1024*1024,  # 25MB
        backupCount=10,
        encoding='utf-8'
    )
    workflow_handler.setFormatter(JSONFormatter())
    workflow_logger.addHandler(workflow_handler)
    workflow_logger.setLevel(logging.INFO)
    workflow_logger.propagate = False
    
    # External services logger (Gemini, Edge TTS, etc.)
    external_logger = logging.getLogger("aetherium.external")
    external_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / 'external_services.log',
        maxBytes=20*1024*1024,  # 20MB
        backupCount=10,
        encoding='utf-8'
    )
    external_handler.setFormatter(JSONFormatter())
    external_logger.addHandler(external_handler)
    external_logger.setLevel(logging.INFO)
    external_logger.propagate = False


def get_logger(name: str, **kwargs) -> logging.Logger:
    """Get a logger with optional context"""
    logger = logging.getLogger(name)
    
    # Add context to logger if provided
    if kwargs:
        class ContextAdapter(logging.LoggerAdapter):
            def process(self, msg, kwargs):
                return msg, kwargs
        
        return ContextAdapter(logger, kwargs)
    
    return logger


def log_with_context(logger: logging.Logger, level: int, message: str, **context):
    """Log a message with additional context"""
    extra = {}
    for key, value in context.items():
        extra[key] = value
    
    logger.log(level, message, extra=extra)