"""
SMS Handler
The Scribe's Text Message Gateway
"""

import asyncio
import logging
import time
import re
from typing import Dict, Optional, List, Any
from dataclasses import dataclass
import httpx

logger = logging.getLogger("aetherium.sms")

@dataclass
class SMSMessage:
    id: str
    modem_id: str
    phone_number: str
    content: str
    direction: str  # 'incoming' or 'outgoing'
    timestamp: float
    status: str = 'pending'
    session_id: Optional[int] = None
    user_id: Optional[int] = None

class SMSHandler:
    """Handles SMS messaging and monitoring"""
    
    def __init__(self, modem_controller):
        self.modem_controller = modem_controller
        self.backend_url = "http://backend-api:8000"
        self.http_client = httpx.AsyncClient()
        self.running = False
        self.monitoring_task = None
        self.message_queue = asyncio.Queue()
        self.processing_task = None
        
        # SMS monitoring state
        self.last_check_time = {}  # Per modem
        self.pending_confirmations = {}  # For payment confirmations
        
    async def start(self):
        """Start SMS handler"""
        logger.info("📱 Starting SMS handler...")
        
        self.running = True
        
        # Start monitoring and processing tasks
        self.monitoring_task = asyncio.create_task(self._monitor_sms())
        self.processing_task = asyncio.create_task(self._process_sms_queue())
        
        logger.info("✅ SMS handler started")
    
    async def stop(self):
        """Stop SMS handler"""
        logger.info("📱 Stopping SMS handler...")
        
        self.running = False
        
        # Cancel tasks
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
            except asyncio.CancelledError:
                pass
        
        await self.http_client.aclose()
        
        logger.info("📱 SMS handler stopped")
    
    async def _monitor_sms(self):
        """Monitor incoming SMS messages"""
        logger.info("🔍 Starting SMS monitoring...")
        
        while self.running:
            try:
                for modem_id, modem in self.modem_controller.modems.items():
                    if modem.status.value == "idle" or modem.status.value == "busy":
                        await self._check_incoming_sms(modem_id)
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in SMS monitoring: {e}")
                await asyncio.sleep(10)
        
        logger.info("🔍 SMS monitoring stopped")
    
    async def _check_incoming_sms(self, modem_id: str):
        """Check for incoming SMS on specific modem"""
        try:
            modem = self.modem_controller.modems.get(modem_id)
            if not modem or not modem.serial_connection:
                return
            
            # Send AT command to list unread messages
            response = await self.modem_controller._send_at_command(modem, 'AT+CMGL="REC UNREAD"')
            
            if response and "+CMGL:" in response:
                messages = self._parse_sms_list(response)
                
                for msg_data in messages:
                    await self._process_incoming_sms(modem_id, msg_data)
                    
                    # Delete processed message from modem
                    await self.modem_controller._send_at_command(
                        modem, f'AT+CMGD={msg_data["index"]}'
                    )
                    
        except Exception as e:
            logger.error(f"Error checking SMS on {modem_id}: {e}")
    
    def _parse_sms_list(self, response: str) -> List[Dict[str, Any]]:
        """Parse SMS list response"""
        messages = []
        lines = response.split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            if line.startswith('+CMGL:'):
                try:
                    # Parse header: +CMGL: index,"status","sender","","timestamp"
                    parts = line.split(',')
                    index = int(parts[0].split(':')[1].strip())
                    sender = parts[2].strip().strip('"')
                    timestamp = parts[4].strip().strip('"') if len(parts) > 4 else ""
                    
                    # Next line should contain the message content
                    if i + 1 < len(lines):
                        content = lines[i + 1].strip()
                        
                        messages.append({
                            "index": index,
                            "sender": sender,
                            "content": content,
                            "timestamp": timestamp
                        })
                    
                    i += 2  # Skip content line
                except Exception as e:
                    logger.error(f"Error parsing SMS line: {line}, error: {e}")
                    i += 1
            else:
                i += 1
        
        return messages
    
    async def _process_incoming_sms(self, modem_id: str, msg_data: Dict[str, Any]):
        """Process incoming SMS message"""
        try:
            # Create SMS message object
            sms_message = SMSMessage(
                id=f"sms_{int(time.time() * 1000)}_{modem_id}",
                modem_id=modem_id,
                phone_number=msg_data["sender"],
                content=msg_data["content"],
                direction="incoming",
                timestamp=time.time(),
                status="received"
            )
            
            # Add to processing queue
            await self.message_queue.put(sms_message)
            
            logger.info(f"📱 Received SMS from {msg_data['sender']} on {modem_id}")
            
        except Exception as e:
            logger.error(f"Error processing incoming SMS: {e}")
    
    async def _process_sms_queue(self):
        """Process SMS messages from queue"""
        logger.info("🔄 Starting SMS processing queue...")
        
        while self.running:
            try:
                # Get message from queue
                sms_message = await asyncio.wait_for(
                    self.message_queue.get(), timeout=1.0
                )
                
                if sms_message.direction == "incoming":
                    await self._handle_incoming_sms(sms_message)
                elif sms_message.direction == "outgoing":
                    await self._handle_outgoing_sms(sms_message)
                
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing SMS queue: {e}")
                await asyncio.sleep(1)
        
        logger.info("🔄 SMS processing queue stopped")
    
    async def _handle_incoming_sms(self, sms_message: SMSMessage):
        """Handle incoming SMS message"""
        try:
            # Get modem info
            modem = self.modem_controller.modems.get(sms_message.modem_id)
            if not modem:
                return
            
            company_number = modem.phone_number
            
            # Check if this is a payment confirmation SMS
            if await self._check_payment_confirmation(sms_message, company_number):
                return
            
            # Get user info by company number
            user_info = await self._get_user_by_company_number(company_number)
            if user_info:
                sms_message.user_id = user_info["id"]
                
                # Create or get SMS session
                session_info = await self._get_or_create_sms_session(sms_message, user_info)
                if session_info:
                    sms_message.session_id = session_info["id"]
                    
                    # Process SMS through AI
                    await self._process_sms_with_ai(sms_message, session_info)
            
            # Notify backend about SMS
            await self._notify_backend_sms(sms_message)
            
        except Exception as e:
            logger.error(f"Error handling incoming SMS: {e}")
    
    async def _check_payment_confirmation(self, sms_message: SMSMessage, company_number: str) -> bool:
        """Check if SMS is a payment confirmation"""
        try:
            # Check if there are any sessions waiting for payment confirmation
            response = await self.http_client.get(
                f"{self.backend_url}/api/sessions/awaiting-payment/{company_number}"
            )
            
            if response.status_code == 200:
                sessions = response.json()
                
                for session in sessions:
                    # Send SMS content to AI for payment analysis
                    analysis_result = await self._analyze_payment_sms(
                        sms_message.content, session["id"]
                    )
                    
                    if analysis_result and analysis_result.get("is_payment_confirmation"):
                        # Process payment confirmation
                        await self._process_payment_confirmation(
                            sms_message, session, analysis_result
                        )
                        return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking payment confirmation: {e}")
            return False
    
    async def _analyze_payment_sms(self, sms_content: str, session_id: int) -> Optional[Dict[str, Any]]:
        """Analyze SMS for payment confirmation using AI"""
        try:
            analysis_data = {
                "sms_content": sms_content,
                "session_id": session_id,
                "analysis_type": "payment_confirmation"
            }
            
            response = await self.http_client.post(
                f"{self.backend_url}/api/ai/analyze-sms",
                json=analysis_data
            )
            
            if response.status_code == 200:
                return response.json()
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing payment SMS: {e}")
            return None
    
    async def _process_payment_confirmation(self, sms_message: SMSMessage, session: Dict[str, Any], 
                                         analysis_result: Dict[str, Any]):
        """Process payment confirmation"""
        try:
            confirmation_data = {
                "session_id": session["id"],
                "sms_content": sms_message.content,
                "sender_number": sms_message.phone_number,
                "analysis_result": analysis_result,
                "confirmed": analysis_result.get("status") == "CONFIRMED"
            }
            
            response = await self.http_client.post(
                f"{self.backend_url}/api/payments/confirm-sms",
                json=confirmation_data
            )
            
            if response.status_code == 200:
                logger.info(f"Processed payment confirmation for session {session['id']}")
            
        except Exception as e:
            logger.error(f"Error processing payment confirmation: {e}")
    
    async def _get_user_by_company_number(self, company_number: str) -> Optional[Dict[str, Any]]:
        """Get user info by company number"""
        try:
            response = await self.http_client.get(
                f"{self.backend_url}/api/users/by-company-number/{company_number}"
            )
            
            if response.status_code == 200:
                return response.json()
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user by company number: {e}")
            return None
    
    async def _get_or_create_sms_session(self, sms_message: SMSMessage, user_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get or create SMS session"""
        try:
            # Check for existing active SMS session
            response = await self.http_client.get(
                f"{self.backend_url}/api/sessions/active-sms/{user_info['id']}/{sms_message.phone_number}"
            )
            
            if response.status_code == 200:
                return response.json()
            
            # Create new SMS session
            session_data = {
                "session_type": "sms",
                "caller_id": sms_message.phone_number,
                "company_number": user_info.get("company_number"),
                "user_id": user_info["id"]
            }
            
            response = await self.http_client.post(
                f"{self.backend_url}/api/sessions/create",
                json=session_data
            )
            
            if response.status_code == 200:
                return response.json()
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting/creating SMS session: {e}")
            return None
    
    async def _process_sms_with_ai(self, sms_message: SMSMessage, session_info: Dict[str, Any]):
        """Process SMS through AI"""
        try:
            ai_request = {
                "session_id": session_info["id"],
                "user_input": sms_message.content,
                "input_type": "sms",
                "sender_number": sms_message.phone_number
            }
            
            response = await self.http_client.post(
                f"{self.backend_url}/api/ai/process-sms",
                json=ai_request
            )
            
            if response.status_code == 200:
                ai_response = response.json()
                
                # Send SMS reply if AI generated one
                if ai_response.get("reply_sms"):
                    await self.send_sms(
                        to_number=sms_message.phone_number,
                        content=ai_response["reply_sms"],
                        from_number=session_info.get("company_number"),
                        session_id=session_info["id"]
                    )
                
                # Execute workflow actions
                if ai_response.get("actions"):
                    await self._execute_sms_actions(ai_response["actions"], session_info)
                    
        except Exception as e:
            logger.error(f"Error processing SMS with AI: {e}")
    
    async def _execute_sms_actions(self, actions: List[Dict[str, Any]], session_info: Dict[str, Any]):
        """Execute SMS-triggered workflow actions"""
        try:
            for action in actions:
                action_type = action.get("type")
                
                if action_type == "send_sms":
                    await self.send_sms(
                        to_number=action.get("to_number"),
                        content=action.get("content"),
                        from_number=session_info.get("company_number"),
                        session_id=session_info["id"]
                    )
                elif action_type == "initiate_call":
                    # Trigger call via call handler
                    call_data = {
                        "to_number": action.get("to_number"),
                        "from_number": session_info.get("company_number"),
                        "session_id": session_info["id"],
                        "user_id": session_info["user_id"]
                    }
                    
                    await self.http_client.post(
                        "http://localhost:8001/initiate-call",
                        json=call_data
                    )
                
        except Exception as e:
            logger.error(f"Error executing SMS actions: {e}")
    
    async def send_sms(self, to_number: str, content: str, from_number: Optional[str] = None,
                      session_id: Optional[int] = None, priority: str = "normal") -> bool:
        """Send SMS message"""
        try:
            # Find appropriate modem
            modem_id = None
            
            if from_number:
                modem_id = self.modem_controller.get_modem_by_number(from_number)
            
            if not modem_id:
                available_modems = self.modem_controller.get_available_modems()
                if not available_modems:
                    logger.error("No available modems for SMS sending")
                    return False
                modem_id = available_modems[0]
            
            # Send SMS via modem controller
            success = await self.modem_controller.send_sms(modem_id, to_number, content)
            
            if success:
                # Create outgoing SMS record
                sms_message = SMSMessage(
                    id=f"sms_out_{int(time.time() * 1000)}_{modem_id}",
                    modem_id=modem_id,
                    phone_number=to_number,
                    content=content,
                    direction="outgoing",
                    timestamp=time.time(),
                    status="sent",
                    session_id=session_id
                )
                
                # Notify backend
                await self._notify_backend_sms(sms_message)
                
                logger.info(f"📱 Sent SMS to {to_number} via {modem_id}")
                
            return success
            
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return False
    
    async def _handle_outgoing_sms(self, sms_message: SMSMessage):
        """Handle outgoing SMS message"""
        try:
            # Notify backend about outgoing SMS
            await self._notify_backend_sms(sms_message)
            
        except Exception as e:
            logger.error(f"Error handling outgoing SMS: {e}")
    
    async def _notify_backend_sms(self, sms_message: SMSMessage):
        """Notify backend about SMS message"""
        try:
            sms_data = {
                "message_id": sms_message.id,
                "modem_id": sms_message.modem_id,
                "phone_number": sms_message.phone_number,
                "content": sms_message.content,
                "direction": sms_message.direction,
                "timestamp": sms_message.timestamp,
                "status": sms_message.status,
                "session_id": sms_message.session_id,
                "user_id": sms_message.user_id
            }
            
            await self.http_client.post(
                f"{self.backend_url}/api/sms/message",
                json=sms_data
            )
            
        except Exception as e:
            logger.error(f"Error notifying backend about SMS: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get SMS handler statistics"""
        return {
            "running": self.running,
            "queue_size": self.message_queue.qsize(),
            "monitored_modems": len(self.modem_controller.modems),
            "pending_confirmations": len(self.pending_confirmations)
        }