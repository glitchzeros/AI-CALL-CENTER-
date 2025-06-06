"""
Aetherium Backend API
The Scribe's Central Nervous System
"""

from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
import logging
import os
from datetime import datetime

from database.connection import get_database, init_database
from routers import auth, users, subscriptions, workflows, sessions, statistics, payments, telegram_integration
from services.dream_journal import DreamJournalService
from services.gemini_client import GeminiClient
from services.edge_tts_client import EdgeTTSClient
from utils.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Initialize services
dream_journal_service = DreamJournalService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("🌟 Aetherium Backend Starting - The Scribe Awakens")
    
    # Initialize database
    await init_database()
    
    # Start background services
    await dream_journal_service.start_nightly_analysis()
    
    logger.info("✨ Aetherium Backend Ready - The Scribe is Listening")
    
    yield
    
    # Cleanup
    logger.info("🌙 Aetherium Backend Shutting Down - The Scribe Rests")
    await dream_journal_service.stop()

# Create FastAPI app
app = FastAPI(
    title="Aetherium API",
    description="The Scribe's Central Intelligence - AI Call Center Platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(subscriptions.router, prefix="/api/subscriptions", tags=["Subscriptions"])
app.include_router(workflows.router, prefix="/api/workflows", tags=["Workflows"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Sessions"])
app.include_router(statistics.router, prefix="/api/statistics", tags=["Statistics"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(telegram_integration.router, prefix="/api/telegram", tags=["Telegram"])

@app.get("/")
async def root():
    """Root endpoint - The Scribe's greeting"""
    return {
        "message": "Welcome to Aetherium - Where AI Scribes Dwell",
        "status": "The Scribe is Ready",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db = await get_database()
        await db.execute("SELECT 1")
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "database": "connected",
                "gemini_api": "configured" if os.getenv("GEMINI_API_KEY") else "not_configured",
                "edge_tts": "available",
                "dream_journal": "active" if dream_journal_service.is_running else "inactive"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.post("/api/click/callback")
async def click_payment_callback(request: Request, background_tasks: BackgroundTasks):
    """
    Click API payment callback endpoint
    Handles payment confirmations from Click payment gateway
    """
    try:
        form_data = await request.form()
        
        # Extract Click API parameters
        click_trans_id = form_data.get("click_trans_id")
        service_id = form_data.get("service_id")
        click_paydoc_id = form_data.get("click_paydoc_id")
        merchant_trans_id = form_data.get("merchant_trans_id")
        amount = float(form_data.get("amount", 0))
        action = int(form_data.get("action", 0))
        error = int(form_data.get("error", 0))
        error_note = form_data.get("error_note", "")
        sign_time = form_data.get("sign_time")
        sign_string = form_data.get("sign_string")
        
        logger.info(f"Click callback received: trans_id={click_trans_id}, action={action}, error={error}")
        
        # Process payment in background
        from services.payment_service import PaymentService
        payment_service = PaymentService()
        
        background_tasks.add_task(
            payment_service.process_click_callback,
            click_trans_id=click_trans_id,
            service_id=service_id,
            click_paydoc_id=click_paydoc_id,
            merchant_trans_id=merchant_trans_id,
            amount=amount,
            action=action,
            error=error,
            error_note=error_note,
            sign_time=sign_time,
            sign_string=sign_string
        )
        
        # Return success response to Click
        return {
            "click_trans_id": click_trans_id,
            "merchant_trans_id": merchant_trans_id,
            "error": 0,
            "error_note": "Success"
        }
        
    except Exception as e:
        logger.error(f"Click callback error: {e}")
        return {
            "error": -1,
            "error_note": "Internal server error"
        }

@app.websocket("/ws/session/{session_id}")
async def websocket_session_endpoint(websocket, session_id: str):
    """
    WebSocket endpoint for real-time session updates
    Used by the frontend to receive live session data
    """
    from services.websocket_manager import WebSocketManager
    
    manager = WebSocketManager()
    await manager.connect(websocket, session_id)
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            # Process any client messages if needed
            
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
    finally:
        await manager.disconnect(websocket, session_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)