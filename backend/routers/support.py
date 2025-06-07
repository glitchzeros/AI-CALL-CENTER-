"""
Support Chat API Router
Handles Gemini-powered support chat functionality
"""

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import List, Optional
import logging
from datetime import datetime

from services.gemini_client import GeminiClient
from routers.auth import get_current_user
from models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/support", tags=["support"])

class ChatMessage(BaseModel):
    message: str
    language: str = "en"

class ChatResponse(BaseModel):
    response: str
    timestamp: datetime
    language: str

# Initialize Gemini client
gemini_client = GeminiClient()

# Aetherium platform knowledge base for the AI assistant
AETHERIUM_SYSTEM_PROMPT = """You are an expert AI assistant for the Aetherium platform, a sophisticated AI call center system. You have deep knowledge about:

PLATFORM OVERVIEW:
- Aetherium enables businesses to deploy AI agents called "Scribes" for automated conversations
- Supports voice calls, SMS, and Telegram across 40 concurrent sessions
- Uses Google Gemini 2.0 Flash for AI processing
- Features a unique "coffee paper" aesthetic UI design

KEY FEATURES:
1. Visual Workflow Builder ("Invocation Editor"):
   - Drag-and-drop interface for creating AI behaviors
   - Nodes called "Invocations" that define actions
   - Connection lines called "Threads of Logic"
   - Configuration panels called "Configuration Scrolls"

2. Core Invocations:
   - "The Payment Ritual": Complex payment flow with SMS confirmation
   - "The Messenger": Send SMS messages
   - "The Telegram Channeler": Telegram bot integration  
   - "The Final Word": Hang up calls
   - "The Scribe's Reply": AI conversation responses

3. Subscription Tiers:
   - Apprentice ($20): 4,000 tokens context memory (~5 mins)
   - Journeyman ($50): 32,000 tokens context memory (~1 hour)
   - Master Scribe ($100): Unlimited tokens for session duration

4. Hardware Requirements:
   - 64GB RAM, NVIDIA Tesla V100 GPU
   - Up to 40 SIM800C GSM modems with dual USB connections
   - 15 PCI 1x slots for USB expansion

5. Technical Architecture:
   - Frontend: React with coffee paper theme
   - Backend: FastAPI with PostgreSQL
   - Modem Manager: Python service for GSM control
   - Telegram Bot: Python service for messaging
   - Single command deployment: docker-compose up -d

6. Audio Processing:
   - Voice Activity Detection (VAD)
   - Noise reduction and audio filtering
   - Microsoft Edge TTS with dynamic voice modulation
   - Speech-to-text for conversation context

7. Analytics & Monitoring:
   - Real-time dashboard with session statistics
   - Call history with AI-generated summaries
   - Performance trends and outcome analysis
   - "The Scribe's Dream Journal" for autonomous insights

8. Security Features:
   - JWT authentication
   - Encrypted storage for sensitive data
   - Input validation and sanitization
   - Audit logging

MULTILINGUAL SUPPORT:
- English, Uzbek, and Russian translations
- Dynamic language switching
- Persistent language preferences

COFFEE PAPER AESTHETIC:
- Color palette: beige, khaki, tan, coffee brown, sienna
- Typography: Cinzel Decorative for headings, Vollkorn for body
- Audio feedback: paper sliding, pen scratching, book closing sounds
- Visual aging effects that develop with usage

Always provide helpful, accurate information about Aetherium. If asked about features not mentioned above, politely explain that you can help with the documented features. Respond in the user's preferred language when possible."""

@router.post("/chat", response_model=ChatResponse)
async def chat_with_support(
    chat_message: ChatMessage,
    current_user: User = Depends(get_current_user)
):
    """
    Handle support chat messages using Gemini AI
    """
    try:
        # Construct the full prompt with system context and user message
        full_prompt = f"{AETHERIUM_SYSTEM_PROMPT}\n\nUser Question: {chat_message.message}\n\nPlease respond in {chat_message.language} language if possible."
        
        # Get response from Gemini
        response = await gemini_client.generate_text_response(
            prompt=full_prompt,
            max_tokens=1000,
            temperature=0.7
        )
        
        if not response:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate AI response"
            )
        
        logger.info(f"Support chat response generated for user {current_user.id}")
        
        return ChatResponse(
            response=response,
            timestamp=datetime.utcnow(),
            language=chat_message.language
        )
        
    except Exception as e:
        logger.error(f"Error in support chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your message"
        )

@router.get("/health")
async def support_health_check():
    """
    Health check endpoint for support service
    """
    try:
        # Test Gemini client connectivity
        test_response = await gemini_client.generate_text_response(
            prompt="Hello, this is a health check.",
            max_tokens=10
        )
        
        return {
            "status": "healthy",
            "gemini_available": bool(test_response),
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Support health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "gemini_available": False,
            "error": str(e),
            "timestamp": datetime.utcnow()
        }