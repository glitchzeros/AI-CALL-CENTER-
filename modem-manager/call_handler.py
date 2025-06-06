"""
Call Handler
The Scribe's Voice Communication Manager
"""

import asyncio
import logging
import time
import uuid
from typing import Dict, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import httpx

logger = logging.getLogger("aetherium.calls")

class CallStatus(Enum):
    INCOMING = "incoming"
    RINGING = "ringing"
    ACTIVE = "active"
    ENDING = "ending"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class CallSession:
    call_id: str
    modem_id: str
    caller_id: Optional[str] = None
    company_number: Optional[str] = None
    user_id: Optional[int] = None
    session_id: Optional[int] = None
    status: CallStatus = CallStatus.INCOMING
    started_at: float = field(default_factory=time.time)
    ended_at: Optional[float] = None
    duration_seconds: Optional[int] = None
    audio_buffer: list = field(default_factory=list)
    context_history: list = field(default_factory=list)
    workflow_state: Dict[str, Any] = field(default_factory=dict)

class CallHandler:
    """Manages voice call sessions and audio processing"""
    
    def __init__(self, modem_controller, audio_processor):
        self.modem_controller = modem_controller
        self.audio_processor = audio_processor
        self.active_calls: Dict[str, CallSession] = {}
        self.backend_url = "http://backend-api:8000"
        self.http_client = httpx.AsyncClient()
        self.is_running = False
        self.monitoring_task = None
        
    async def start(self):
        """Start call handler"""
        logger.info("📞 Starting call handler...")
        
        self.is_running = True
        self.monitoring_task = asyncio.create_task(self._monitor_calls())
        
        logger.info("✅ Call handler started")
    
    async def stop(self):
        """Stop call handler"""
        logger.info("📞 Stopping call handler...")
        
        self.is_running = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        # End all active calls
        for call_id in list(self.active_calls.keys()):
            await self.end_call(call_id)
        
        await self.http_client.aclose()
        
        logger.info("📞 Call handler stopped")
    
    async def _monitor_calls(self):
        """Monitor active calls and handle audio processing"""
        logger.info("🔍 Starting call monitoring...")
        
        while self.is_running:
            try:
                for call_id, call_session in list(self.active_calls.items()):
                    if call_session.status == CallStatus.ACTIVE:
                        await self._process_call_audio(call_session)
                
                await asyncio.sleep(0.1)  # 100ms monitoring interval
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in call monitoring: {e}")
                await asyncio.sleep(1)
        
        logger.info("🔍 Call monitoring stopped")
    
    async def handle_incoming_call(self, modem_id: str, caller_id: Optional[str] = None) -> str:
        """Handle incoming call"""
        call_id = str(uuid.uuid4())
        
        try:
            # Get modem info
            modem = self.modem_controller.modems.get(modem_id)
            if not modem:
                logger.error(f"Modem {modem_id} not found for incoming call")
                return None
            
            # Create call session
            call_session = CallSession(
                call_id=call_id,
                modem_id=modem_id,
                caller_id=caller_id,
                company_number=modem.phone_number,
                status=CallStatus.INCOMING
            )
            
            self.active_calls[call_id] = call_session
            
            # Notify backend about incoming call
            await self._notify_backend_call_event(call_session, "incoming")
            
            # Answer the call
            if await self.modem_controller.answer_call(modem_id):
                call_session.status = CallStatus.ACTIVE
                logger.info(f"📞 Answered incoming call {call_id} on {modem_id}")
                
                # Get user and session info from backend
                await self._initialize_call_session(call_session)
                
                # Start conversation
                await self._start_conversation(call_session)
                
            else:
                call_session.status = CallStatus.FAILED
                logger.error(f"❌ Failed to answer call {call_id} on {modem_id}")
            
            return call_id
            
        except Exception as e:
            logger.error(f"Error handling incoming call: {e}")
            if call_id in self.active_calls:
                self.active_calls[call_id].status = CallStatus.FAILED
            return None
    
    async def initiate_call(self, to_number: str, from_number: Optional[str] = None, 
                          session_id: Optional[int] = None, user_id: Optional[int] = None) -> str:
        """Initiate outgoing call"""
        call_id = str(uuid.uuid4())
        
        try:
            # Find available modem
            available_modems = self.modem_controller.get_available_modems()
            if not available_modems:
                logger.error("No available modems for outgoing call")
                return None
            
            # Use specific modem if from_number provided
            modem_id = None
            if from_number:
                modem_id = self.modem_controller.get_modem_by_number(from_number)
            
            if not modem_id:
                modem_id = available_modems[0]
            
            # Create call session
            call_session = CallSession(
                call_id=call_id,
                modem_id=modem_id,
                caller_id=to_number,
                company_number=from_number,
                user_id=user_id,
                session_id=session_id,
                status=CallStatus.RINGING
            )
            
            self.active_calls[call_id] = call_session
            
            # Dial the number
            if await self.modem_controller.dial_number(modem_id, to_number):
                logger.info(f"📞 Initiated outgoing call {call_id} to {to_number}")
                
                # Wait for call to be answered (simplified - in reality would monitor modem responses)
                await asyncio.sleep(2)
                call_session.status = CallStatus.ACTIVE
                
                # Initialize session
                await self._initialize_call_session(call_session)
                
                # Start conversation
                await self._start_conversation(call_session)
                
            else:
                call_session.status = CallStatus.FAILED
                logger.error(f"❌ Failed to dial {to_number}")
            
            return call_id
            
        except Exception as e:
            logger.error(f"Error initiating call: {e}")
            if call_id in self.active_calls:
                self.active_calls[call_id].status = CallStatus.FAILED
            return None
    
    async def hangup_call(self, call_id: str) -> bool:
        """Hang up active call"""
        call_session = self.active_calls.get(call_id)
        if not call_session:
            return False
        
        try:
            call_session.status = CallStatus.ENDING
            
            # Hang up via modem
            success = await self.modem_controller.hangup_call(call_session.modem_id)
            
            # End call session
            await self.end_call(call_id)
            
            logger.info(f"📞 Hung up call {call_id}")
            return success
            
        except Exception as e:
            logger.error(f"Error hanging up call {call_id}: {e}")
            return False
    
    async def end_call(self, call_id: str):
        """End call session and cleanup"""
        call_session = self.active_calls.get(call_id)
        if not call_session:
            return
        
        try:
            # Update call session
            call_session.status = CallStatus.COMPLETED
            call_session.ended_at = time.time()
            call_session.duration_seconds = int(call_session.ended_at - call_session.started_at)
            
            # Notify backend about call end
            await self._notify_backend_call_event(call_session, "ended")
            
            # Generate AI summary
            await self._generate_call_summary(call_session)
            
            # Remove from active calls
            del self.active_calls[call_id]
            
            logger.info(f"📞 Ended call {call_id} (duration: {call_session.duration_seconds}s)")
            
        except Exception as e:
            logger.error(f"Error ending call {call_id}: {e}")
    
    async def _initialize_call_session(self, call_session: CallSession):
        """Initialize call session with backend"""
        try:
            # Get user info by company number
            response = await self.http_client.get(
                f"{self.backend_url}/api/users/by-company-number/{call_session.company_number}"
            )
            
            if response.status_code == 200:
                user_data = response.json()
                call_session.user_id = user_data["id"]
                
                # Create session in backend
                session_data = {
                    "session_type": "voice",
                    "caller_id": call_session.caller_id,
                    "company_number": call_session.company_number,
                    "user_id": call_session.user_id
                }
                
                response = await self.http_client.post(
                    f"{self.backend_url}/api/sessions/create",
                    json=session_data
                )
                
                if response.status_code == 200:
                    session_info = response.json()
                    call_session.session_id = session_info["id"]
                    
                    # Load user's workflow
                    await self._load_user_workflow(call_session)
                    
        except Exception as e:
            logger.error(f"Error initializing call session: {e}")
    
    async def _load_user_workflow(self, call_session: CallSession):
        """Load user's active workflow"""
        try:
            if not call_session.user_id:
                return
            
            response = await self.http_client.get(
                f"{self.backend_url}/api/workflows/active/{call_session.user_id}"
            )
            
            if response.status_code == 200:
                workflow_data = response.json()
                call_session.workflow_state = {
                    "workflow_id": workflow_data["id"],
                    "nodes": workflow_data["workflow_data"]["nodes"],
                    "connections": workflow_data["workflow_data"]["connections"],
                    "current_node": None,
                    "execution_history": []
                }
                
                logger.info(f"Loaded workflow for call {call_session.call_id}")
                
        except Exception as e:
            logger.error(f"Error loading workflow: {e}")
    
    async def _start_conversation(self, call_session: CallSession):
        """Start conversation with greeting"""
        try:
            # Send initial greeting
            greeting = "Hello! I am your AI Scribe. How may I assist you today?"
            
            await self._send_ai_response(call_session, greeting)
            
            # Add to context
            call_session.context_history.append({
                "speaker": "ai",
                "content": greeting,
                "timestamp": time.time()
            })
            
        except Exception as e:
            logger.error(f"Error starting conversation: {e}")
    
    async def _process_call_audio(self, call_session: CallSession):
        """Process audio for active call"""
        try:
            # This is a simplified version - in reality would capture audio from modem
            # For now, we'll simulate audio processing
            
            # Check if there's new audio data (would come from modem audio interface)
            # audio_data = await self._capture_audio_from_modem(call_session.modem_id)
            
            # Process audio through pipeline
            # if audio_data:
            #     processed_audio, metadata = await self.audio_processor.process_audio_stream(
            #         audio_data, {"call_id": call_session.call_id}
            #     )
            #     
            #     if metadata and metadata.get("is_voice"):
            #         # Convert to text and process
            #         await self._process_voice_input(call_session, processed_audio)
            
            pass  # Placeholder for actual audio processing
            
        except Exception as e:
            logger.error(f"Error processing call audio: {e}")
    
    async def _process_voice_input(self, call_session: CallSession, audio_data: bytes):
        """Process voice input from user"""
        try:
            # Convert audio to text (STT)
            text = await self._speech_to_text(audio_data)
            
            if text:
                # Add to context
                call_session.context_history.append({
                    "speaker": "user",
                    "content": text,
                    "timestamp": time.time()
                })
                
                # Process with AI
                await self._process_user_input(call_session, text, audio_data)
                
        except Exception as e:
            logger.error(f"Error processing voice input: {e}")
    
    async def _speech_to_text(self, audio_data: bytes) -> Optional[str]:
        """Convert speech to text"""
        try:
            # This would integrate with STT service (Vosk, etc.)
            # For now, return placeholder
            return "User said something"
            
        except Exception as e:
            logger.error(f"STT error: {e}")
            return None
    
    async def _process_user_input(self, call_session: CallSession, text: str, audio_data: bytes):
        """Process user input through AI and workflow"""
        try:
            # Send to backend for AI processing
            request_data = {
                "session_id": call_session.session_id,
                "user_input": text,
                "audio_data": audio_data.hex() if audio_data else None,
                "context_history": call_session.context_history[-10:],  # Last 10 messages
                "workflow_state": call_session.workflow_state
            }
            
            response = await self.http_client.post(
                f"{self.backend_url}/api/ai/process-input",
                json=request_data
            )
            
            if response.status_code == 200:
                ai_response = response.json()
                
                # Update workflow state
                if "workflow_state" in ai_response:
                    call_session.workflow_state.update(ai_response["workflow_state"])
                
                # Send AI response
                if "response_text" in ai_response:
                    await self._send_ai_response(call_session, ai_response["response_text"])
                    
                    # Add to context
                    call_session.context_history.append({
                        "speaker": "ai",
                        "content": ai_response["response_text"],
                        "timestamp": time.time()
                    })
                
                # Handle workflow actions
                if "actions" in ai_response:
                    await self._execute_workflow_actions(call_session, ai_response["actions"])
                    
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
    
    async def _send_ai_response(self, call_session: CallSession, text: str):
        """Send AI response via TTS"""
        try:
            # Convert text to speech
            audio_data = await self._text_to_speech(text, call_session)
            
            if audio_data:
                # Send audio to modem for playback
                await self._play_audio_to_modem(call_session.modem_id, audio_data)
                
        except Exception as e:
            logger.error(f"Error sending AI response: {e}")
    
    async def _text_to_speech(self, text: str, call_session: CallSession) -> Optional[bytes]:
        """Convert text to speech"""
        try:
            # Send to backend TTS service
            response = await self.http_client.post(
                f"{self.backend_url}/api/tts/synthesize",
                json={
                    "text": text,
                    "language": "en",  # Would be detected from context
                    "voice_settings": {
                        "pitch": "+0%",
                        "rate": "+0%"
                    }
                }
            )
            
            if response.status_code == 200:
                return response.content
            
            return None
            
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return None
    
    async def _play_audio_to_modem(self, modem_id: str, audio_data: bytes):
        """Play audio through modem"""
        try:
            # This would send audio to modem's audio interface
            # Implementation depends on modem audio capabilities
            logger.debug(f"Playing audio to modem {modem_id}")
            
        except Exception as e:
            logger.error(f"Error playing audio to modem: {e}")
    
    async def _execute_workflow_actions(self, call_session: CallSession, actions: list):
        """Execute workflow actions"""
        try:
            for action in actions:
                action_type = action.get("type")
                
                if action_type == "hangup":
                    await self.hangup_call(call_session.call_id)
                elif action_type == "send_sms":
                    await self._send_sms_action(call_session, action)
                elif action_type == "transfer_call":
                    await self._transfer_call_action(call_session, action)
                # Add more action types as needed
                
        except Exception as e:
            logger.error(f"Error executing workflow actions: {e}")
    
    async def _send_sms_action(self, call_session: CallSession, action: dict):
        """Execute SMS sending action"""
        try:
            sms_data = {
                "to_number": action.get("to_number", call_session.caller_id),
                "content": action.get("content", ""),
                "from_number": call_session.company_number,
                "session_id": call_session.session_id
            }
            
            # Send via modem manager SMS handler
            response = await self.http_client.post(
                "http://localhost:8001/send-sms",
                json=sms_data
            )
            
            logger.info(f"SMS action executed for call {call_session.call_id}")
            
        except Exception as e:
            logger.error(f"Error executing SMS action: {e}")
    
    async def _notify_backend_call_event(self, call_session: CallSession, event_type: str):
        """Notify backend about call events"""
        try:
            event_data = {
                "call_id": call_session.call_id,
                "event_type": event_type,
                "session_id": call_session.session_id,
                "modem_id": call_session.modem_id,
                "caller_id": call_session.caller_id,
                "company_number": call_session.company_number,
                "status": call_session.status.value,
                "timestamp": time.time()
            }
            
            await self.http_client.post(
                f"{self.backend_url}/api/calls/event",
                json=event_data
            )
            
        except Exception as e:
            logger.error(f"Error notifying backend: {e}")
    
    async def _generate_call_summary(self, call_session: CallSession):
        """Generate AI summary of the call"""
        try:
            if not call_session.context_history:
                return
            
            summary_data = {
                "session_id": call_session.session_id,
                "context_history": call_session.context_history,
                "call_duration": call_session.duration_seconds,
                "outcome": "completed"  # Would be determined by workflow
            }
            
            response = await self.http_client.post(
                f"{self.backend_url}/api/ai/generate-summary",
                json=summary_data
            )
            
            if response.status_code == 200:
                logger.info(f"Generated summary for call {call_session.call_id}")
                
        except Exception as e:
            logger.error(f"Error generating call summary: {e}")
    
    def get_call_status(self, call_id: str) -> Optional[Dict[str, Any]]:
        """Get call status"""
        call_session = self.active_calls.get(call_id)
        if not call_session:
            return None
        
        return {
            "call_id": call_session.call_id,
            "status": call_session.status.value,
            "caller_id": call_session.caller_id,
            "duration": int(time.time() - call_session.started_at),
            "modem_id": call_session.modem_id
        }