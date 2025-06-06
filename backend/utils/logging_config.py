"""
Logging configuration
The Scribe's Chronicle System
"""

import logging
import logging.handlers
import os
from datetime import datetime

def setup_logging():
    """Setup logging configuration for the Aetherium backend"""
    
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Console handler
            logging.StreamHandler(),
            # File handler with rotation
            logging.handlers.RotatingFileHandler(
                filename=os.path.join(log_dir, 'aetherium.log'),
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
        ]
    )
    
    # Set specific log levels for different modules
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Create specialized loggers
    
    # Session logger for conversation tracking
    session_logger = logging.getLogger("aetherium.sessions")
    session_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, 'sessions.log'),
        maxBytes=50*1024*1024,  # 50MB
        backupCount=10
    )
    session_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    session_logger.addHandler(session_handler)
    session_logger.setLevel(logging.INFO)
    
    # Payment logger for financial transactions
    payment_logger = logging.getLogger("aetherium.payments")
    payment_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, 'payments.log'),
        maxBytes=20*1024*1024,  # 20MB
        backupCount=20  # Keep more payment logs for audit
    )
    payment_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    payment_logger.addHandler(payment_handler)
    payment_logger.setLevel(logging.INFO)
    
    # Dream journal logger for AI insights
    dream_logger = logging.getLogger("aetherium.dreams")
    dream_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, 'dream_journal.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    dream_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    dream_logger.addHandler(dream_handler)
    dream_logger.setLevel(logging.INFO)
    
    # Modem communication logger
    modem_logger = logging.getLogger("aetherium.modems")
    modem_handler = logging.handlers.RotatingFileHandler(
        filename=os.path.join(log_dir, 'modems.log'),
        maxBytes=30*1024*1024,  # 30MB
        backupCount=7
    )
    modem_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    modem_logger.addHandler(modem_handler)
    modem_logger.setLevel(logging.INFO)
    
    logging.info("📜 Aetherium logging system initialized")