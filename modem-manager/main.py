"""
Aetherium Modem Manager
The Scribe's Communication Hardware Controller
"""

import asyncio
import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from modem_controller import ModemController
from audio_processor import AudioProcessor
from sms_handler import SMSHandler
from call_handler import CallHandler
from device_manager import DeviceManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('logs/modem_manager.log')
    ]
)

logger = logging.getLogger(__name__)

# Global managers
device_manager = None
modem_controller = None
audio_processor = None
sms_handler = None
call_handler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global device_manager, modem_controller, audio_processor, sms_handler, call_handler
    
    logger.info("🔌 Aetherium Modem Manager Starting")
    
    try:
        # Initialize device manager
        device_manager = DeviceManager()
        await device_manager.initialize()
        
        # Initialize modem controller
        modem_controller = ModemController(device_manager)
        await modem_controller.initialize()
        
        # Initialize audio processor
        audio_processor = AudioProcessor()
        await audio_processor.initialize()
        
        # Initialize SMS handler
        sms_handler = SMSHandler(modem_controller)
        await sms_handler.start()
        
        # Initialize call handler
        call_handler = CallHandler(modem_controller, audio_processor)
        await call_handler.start()
        
        logger.info("✅ Modem Manager Ready - All systems operational")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize modem manager: {e}")
        raise
    finally:
        # Cleanup
        logger.info("🔌 Modem Manager Shutting Down")
        
        if call_handler:
            await call_handler.stop()
        if sms_handler:
            await sms_handler.stop()
        if audio_processor:
            await audio_processor.cleanup()
        if modem_controller:
            await modem_controller.cleanup()
        if device_manager:
            await device_manager.cleanup()

# Create FastAPI app
app = FastAPI(
    title="Aetherium Modem Manager",
    description="The Scribe's Communication Hardware Controller",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Aetherium Modem Manager",
        "status": "The Scribe's Voice is Ready",
        "modems_connected": len(modem_controller.modems) if modem_controller else 0
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        modem_count = len(modem_controller.modems) if modem_controller else 0
        active_calls = len(call_handler.active_calls) if call_handler else 0
        
        return {
            "status": "healthy",
            "modems_connected": modem_count,
            "active_calls": active_calls,
            "audio_processor": "ready" if audio_processor else "not_ready",
            "sms_handler": "running" if sms_handler and sms_handler.running else "stopped"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.get("/modems")
async def get_modems():
    """Get list of connected modems"""
    if not modem_controller:
        raise HTTPException(status_code=503, detail="Modem controller not initialized")
    
    return {
        "modems": [
            {
                "id": modem.device_id,
                "control_port": modem.control_port,
                "audio_port": modem.audio_port,
                "phone_number": modem.phone_number,
                "status": modem.status,
                "signal_strength": modem.signal_strength
            }
            for modem in modem_controller.modems.values()
        ]
    }

@app.post("/send-sms")
async def send_sms(sms_data: dict):
    """Send SMS message"""
    if not sms_handler:
        raise HTTPException(status_code=503, detail="SMS handler not initialized")
    
    try:
        result = await sms_handler.send_sms(
            to_number=sms_data["to_number"],
            content=sms_data["content"],
            from_number=sms_data.get("from_number"),
            session_id=sms_data.get("session_id"),
            priority=sms_data.get("priority", "normal")
        )
        
        return {"success": result, "message": "SMS sent" if result else "SMS failed"}
        
    except Exception as e:
        logger.error(f"SMS sending error: {e}")
        raise HTTPException(status_code=500, detail="Failed to send SMS")

@app.post("/initiate-call")
async def initiate_call(call_data: dict):
    """Initiate outgoing call"""
    if not call_handler:
        raise HTTPException(status_code=503, detail="Call handler not initialized")
    
    try:
        call_id = await call_handler.initiate_call(
            to_number=call_data["to_number"],
            from_number=call_data.get("from_number"),
            session_id=call_data.get("session_id"),
            user_id=call_data.get("user_id")
        )
        
        return {"success": True, "call_id": call_id}
        
    except Exception as e:
        logger.error(f"Call initiation error: {e}")
        raise HTTPException(status_code=500, detail="Failed to initiate call")

@app.post("/hangup-call/{call_id}")
async def hangup_call(call_id: str):
    """Hang up active call"""
    if not call_handler:
        raise HTTPException(status_code=503, detail="Call handler not initialized")
    
    try:
        result = await call_handler.hangup_call(call_id)
        return {"success": result}
        
    except Exception as e:
        logger.error(f"Call hangup error: {e}")
        raise HTTPException(status_code=500, detail="Failed to hang up call")

@app.get("/active-calls")
async def get_active_calls():
    """Get list of active calls"""
    if not call_handler:
        raise HTTPException(status_code=503, detail="Call handler not initialized")
    
    return {
        "active_calls": [
            {
                "call_id": call_id,
                "modem_id": call.modem_id,
                "caller_id": call.caller_id,
                "started_at": call.started_at.isoformat(),
                "status": call.status
            }
            for call_id, call in call_handler.active_calls.items()
        ]
    }

@app.get("/audio-devices")
async def get_audio_devices():
    """Get available audio devices"""
    if not audio_processor:
        raise HTTPException(status_code=503, detail="Audio processor not initialized")
    
    return audio_processor.get_available_devices()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)