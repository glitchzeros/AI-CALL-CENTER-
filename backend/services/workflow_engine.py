"""
Workflow Execution Engine
The Scribe's Invocation Interpreter
"""

import asyncio
import logging
import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from models.workflow import ScribeWorkflow
from models.session import CommunicationSession
from services.gemini_client import GeminiClient
from services.edge_tts_client import EdgeTTSClient
from services.sms_service import SMSService
from services.payment_service import PaymentService

logger = logging.getLogger("aetherium.workflow")

class InvocationType(Enum):
    PAYMENT_RITUAL = "payment_ritual"
    SEND_SMS = "send_sms"
    TELEGRAM_SEND = "telegram_send"
    HANG_UP = "hang_up"
    AI_RESPONSE = "ai_response"

class ExecutionStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING = "waiting"

@dataclass
class ExecutionContext:
    session_id: int
    user_id: int
    workflow_id: int
    current_node_id: Optional[str] = None
    execution_history: List[Dict[str, Any]] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    status: ExecutionStatus = ExecutionStatus.PENDING
    started_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)

@dataclass
class InvocationResult:
    success: bool
    output_data: Dict[str, Any] = field(default_factory=dict)
    next_nodes: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    requires_wait: bool = False
    wait_condition: Optional[str] = None

class WorkflowEngine:
    """Executes workflow invocations and manages session state"""
    
    def __init__(self, db_session, gemini_client: GeminiClient, edge_tts_client: EdgeTTSClient,
                 sms_service: SMSService, payment_service: PaymentService):
        self.db = db_session
        self.gemini_client = gemini_client
        self.edge_tts_client = edge_tts_client
        self.sms_service = sms_service
        self.payment_service = payment_service
        
        # Active execution contexts
        self.active_contexts: Dict[int, ExecutionContext] = {}
        
        # Invocation handlers
        self.invocation_handlers = {
            InvocationType.PAYMENT_RITUAL: self._execute_payment_ritual,
            InvocationType.SEND_SMS: self._execute_send_sms,
            InvocationType.TELEGRAM_SEND: self._execute_telegram_send,
            InvocationType.HANG_UP: self._execute_hang_up,
            InvocationType.AI_RESPONSE: self._execute_ai_response,
        }
    
    async def start_workflow_execution(self, session_id: int, user_id: int, 
                                     workflow_id: int) -> ExecutionContext:
        """Start workflow execution for a session"""
        try:
            # Create execution context
            context = ExecutionContext(
                session_id=session_id,
                user_id=user_id,
                workflow_id=workflow_id
            )
            
            self.active_contexts[session_id] = context
            
            # Load workflow
            workflow = await self._load_workflow(workflow_id)
            if not workflow:
                context.status = ExecutionStatus.FAILED
                return context
            
            # Find entry point (node with no incoming connections)
            entry_node = self._find_entry_node(workflow.workflow_data)
            if entry_node:
                context.current_node_id = entry_node["id"]
                context.status = ExecutionStatus.RUNNING
                
                # Execute entry node
                await self._execute_node(context, entry_node, workflow.workflow_data)
            
            logger.info(f"Started workflow execution for session {session_id}")
            return context
            
        except Exception as e:
            logger.error(f"Error starting workflow execution: {e}")
            if session_id in self.active_contexts:
                self.active_contexts[session_id].status = ExecutionStatus.FAILED
            raise
    
    async def process_user_input(self, session_id: int, user_input: str, 
                               input_type: str = "text", metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user input through active workflow"""
        try:
            context = self.active_contexts.get(session_id)
            if not context:
                # No active workflow, create default AI response
                return await self._create_default_response(session_id, user_input)
            
            context.last_activity = time.time()
            
            # Add user input to context
            context.variables["last_user_input"] = user_input
            context.variables["last_input_type"] = input_type
            context.variables["last_input_metadata"] = metadata or {}
            
            # Load workflow
            workflow = await self._load_workflow(context.workflow_id)
            if not workflow:
                return {"error": "Workflow not found"}
            
            # Process input based on current workflow state
            if context.status == ExecutionStatus.WAITING:
                # Handle waiting state (e.g., payment confirmation)
                return await self._handle_waiting_state(context, user_input, workflow.workflow_data)
            elif context.status == ExecutionStatus.RUNNING:
                # Continue workflow execution
                return await self._continue_workflow(context, user_input, workflow.workflow_data)
            else:
                # Workflow not active, create default response
                return await self._create_default_response(session_id, user_input)
                
        except Exception as e:
            logger.error(f"Error processing user input: {e}")
            return {"error": "Failed to process input"}
    
    async def _load_workflow(self, workflow_id: int) -> Optional[ScribeWorkflow]:
        """Load workflow from database"""
        try:
            from sqlalchemy import select
            result = await self.db.execute(
                select(ScribeWorkflow).where(ScribeWorkflow.id == workflow_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error loading workflow: {e}")
            return None
    
    def _find_entry_node(self, workflow_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find the entry node (no incoming connections)"""
        nodes = workflow_data.get("nodes", [])
        connections = workflow_data.get("connections", [])
        
        # Get all nodes that have incoming connections
        target_nodes = {conn["to"] for conn in connections}
        
        # Find nodes without incoming connections
        entry_nodes = [node for node in nodes if node["id"] not in target_nodes]
        
        # Return first entry node (could be enhanced to handle multiple entry points)
        return entry_nodes[0] if entry_nodes else None
    
    async def _execute_node(self, context: ExecutionContext, node: Dict[str, Any], 
                          workflow_data: Dict[str, Any]) -> InvocationResult:
        """Execute a workflow node"""
        try:
            node_type = node.get("type")
            node_config = node.get("config", {})
            
            logger.info(f"Executing node {node['id']} of type {node_type}")
            
            # Record execution in history
            execution_record = {
                "node_id": node["id"],
                "node_type": node_type,
                "timestamp": time.time(),
                "status": "started"
            }
            context.execution_history.append(execution_record)
            
            # Get handler for invocation type
            invocation_type = InvocationType(node_type)
            handler = self.invocation_handlers.get(invocation_type)
            
            if not handler:
                raise ValueError(f"No handler for invocation type: {node_type}")
            
            # Execute invocation
            result = await handler(context, node_config)
            
            # Update execution record
            execution_record["status"] = "completed" if result.success else "failed"
            execution_record["result"] = result.output_data
            execution_record["error"] = result.error_message
            
            # Handle result
            if result.success:
                if result.requires_wait:
                    context.status = ExecutionStatus.WAITING
                    context.variables["wait_condition"] = result.wait_condition
                else:
                    # Continue to next nodes
                    await self._continue_to_next_nodes(context, result.next_nodes, workflow_data)
            else:
                # Handle failure
                await self._handle_node_failure(context, node, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error executing node {node['id']}: {e}")
            result = InvocationResult(
                success=False,
                error_message=str(e)
            )
            return result
    
    async def _continue_to_next_nodes(self, context: ExecutionContext, next_node_ids: List[str],
                                    workflow_data: Dict[str, Any]):
        """Continue execution to next nodes"""
        try:
            if not next_node_ids:
                # No next nodes, workflow completed
                context.status = ExecutionStatus.COMPLETED
                logger.info(f"Workflow completed for session {context.session_id}")
                return
            
            # For now, execute first next node (could be enhanced for parallel execution)
            next_node_id = next_node_ids[0]
            next_node = self._find_node_by_id(workflow_data, next_node_id)
            
            if next_node:
                context.current_node_id = next_node_id
                await self._execute_node(context, next_node, workflow_data)
            else:
                logger.error(f"Next node {next_node_id} not found")
                context.status = ExecutionStatus.FAILED
                
        except Exception as e:
            logger.error(f"Error continuing to next nodes: {e}")
            context.status = ExecutionStatus.FAILED
    
    def _find_node_by_id(self, workflow_data: Dict[str, Any], node_id: str) -> Optional[Dict[str, Any]]:
        """Find node by ID"""
        nodes = workflow_data.get("nodes", [])
        return next((node for node in nodes if node["id"] == node_id), None)
    
    def _get_connected_nodes(self, workflow_data: Dict[str, Any], from_node_id: str) -> List[str]:
        """Get nodes connected from the given node"""
        connections = workflow_data.get("connections", [])
        return [conn["to"] for conn in connections if conn["from"] == from_node_id]
    
    # Invocation Handlers
    
    async def _execute_payment_ritual(self, context: ExecutionContext, 
                                    config: Dict[str, Any]) -> InvocationResult:
        """Execute Payment Ritual invocation"""
        try:
            # Get configuration
            bank_card = config.get("bank_card", "")
            reassurance_script = config.get("reassurance_script", "")
            
            # Generate payment instruction
            instruction_text = "Отправляй сюда свои деньги"  # Manual translation
            if bank_card:
                instruction_text += f" на карту {bank_card}"
            
            # Send TTS instruction
            audio_data = await self.edge_tts_client.synthesize_speech(
                text=instruction_text,
                language="ru",
                voice_settings={"pitch": "-5%", "rate": "-10%"}  # Calmer tone
            )
            
            # Set session to awaiting payment confirmation
            context.variables["awaiting_payment"] = True
            context.variables["payment_instruction_sent"] = True
            context.variables["reassurance_script"] = reassurance_script
            
            return InvocationResult(
                success=True,
                output_data={
                    "instruction_sent": True,
                    "audio_data": audio_data,
                    "instruction_text": instruction_text
                },
                requires_wait=True,
                wait_condition="payment_confirmation"
            )
            
        except Exception as e:
            logger.error(f"Error in payment ritual: {e}")
            return InvocationResult(
                success=False,
                error_message=str(e)
            )
    
    async def _execute_send_sms(self, context: ExecutionContext, 
                              config: Dict[str, Any]) -> InvocationResult:
        """Execute Send SMS invocation"""
        try:
            recipient = config.get("recipient", "")
            message = config.get("message", "")
            
            # Replace variables in recipient and message
            recipient = self._replace_variables(recipient, context.variables)
            message = self._replace_variables(message, context.variables)
            
            # Send SMS
            success = await self.sms_service.send_sms(
                to_number=recipient,
                content=message,
                session_id=context.session_id
            )
            
            if success:
                # Get next connected nodes
                workflow = await self._load_workflow(context.workflow_id)
                next_nodes = self._get_connected_nodes(
                    workflow.workflow_data, context.current_node_id
                )
                
                return InvocationResult(
                    success=True,
                    output_data={
                        "sms_sent": True,
                        "recipient": recipient,
                        "message": message
                    },
                    next_nodes=next_nodes
                )
            else:
                return InvocationResult(
                    success=False,
                    error_message="Failed to send SMS"
                )
                
        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            return InvocationResult(
                success=False,
                error_message=str(e)
            )
    
    async def _execute_telegram_send(self, context: ExecutionContext, 
                                   config: Dict[str, Any]) -> InvocationResult:
        """Execute Telegram Send invocation"""
        try:
            # Implementation would integrate with Telegram bot
            # For now, return success placeholder
            
            return InvocationResult(
                success=True,
                output_data={"telegram_sent": True}
            )
            
        except Exception as e:
            logger.error(f"Error sending Telegram: {e}")
            return InvocationResult(
                success=False,
                error_message=str(e)
            )
    
    async def _execute_hang_up(self, context: ExecutionContext, 
                             config: Dict[str, Any]) -> InvocationResult:
        """Execute Hang Up invocation"""
        try:
            # Signal to hang up the call
            context.variables["should_hangup"] = True
            context.status = ExecutionStatus.COMPLETED
            
            return InvocationResult(
                success=True,
                output_data={"call_ended": True}
            )
            
        except Exception as e:
            logger.error(f"Error hanging up: {e}")
            return InvocationResult(
                success=False,
                error_message=str(e)
            )
    
    async def _execute_ai_response(self, context: ExecutionContext, 
                                 config: Dict[str, Any]) -> InvocationResult:
        """Execute AI Response invocation"""
        try:
            # Get user input
            user_input = context.variables.get("last_user_input", "")
            
            # Build prompt with context and configuration
            prompt_parts = []
            
            # Add working instructions
            if config.get("working"):
                prompt_parts.append(f"Instructions: {config['working']}")
            
            # Add context
            if context.execution_history:
                prompt_parts.append("Previous actions in this conversation:")
                for record in context.execution_history[-3:]:  # Last 3 actions
                    prompt_parts.append(f"- {record['node_type']}: {record.get('status', 'unknown')}")
            
            # Add user input
            prompt_parts.append(f"User said: {user_input}")
            prompt_parts.append("Respond naturally and helpfully.")
            
            prompt_text = "\n".join(prompt_parts)
            
            # Get AI response
            ai_response = await self.gemini_client.generate_response(
                prompt_text=prompt_text,
                audio_data=context.variables.get("last_input_metadata", {}).get("audio_data")
            )
            
            if ai_response:
                # Generate TTS
                audio_data = await self.edge_tts_client.synthesize_speech(
                    text=ai_response,
                    language="en"  # Would be detected from context
                )
                
                # Get next nodes
                workflow = await self._load_workflow(context.workflow_id)
                next_nodes = self._get_connected_nodes(
                    workflow.workflow_data, context.current_node_id
                )
                
                return InvocationResult(
                    success=True,
                    output_data={
                        "ai_response": ai_response,
                        "audio_data": audio_data
                    },
                    next_nodes=next_nodes
                )
            else:
                return InvocationResult(
                    success=False,
                    error_message="Failed to generate AI response"
                )
                
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return InvocationResult(
                success=False,
                error_message=str(e)
            )
    
    def _replace_variables(self, text: str, variables: Dict[str, Any]) -> str:
        """Replace variables in text with actual values"""
        try:
            for key, value in variables.items():
                placeholder = f"{{{key}}}"
                if placeholder in text:
                    text = text.replace(placeholder, str(value))
            return text
        except Exception as e:
            logger.error(f"Error replacing variables: {e}")
            return text
    
    async def _handle_waiting_state(self, context: ExecutionContext, user_input: str,
                                  workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle input while workflow is waiting"""
        try:
            wait_condition = context.variables.get("wait_condition")
            
            if wait_condition == "payment_confirmation":
                return await self._handle_payment_confirmation_input(context, user_input, workflow_data)
            
            # Default: continue workflow
            return await self._continue_workflow(context, user_input, workflow_data)
            
        except Exception as e:
            logger.error(f"Error handling waiting state: {e}")
            return {"error": "Failed to handle waiting state"}
    
    async def _handle_payment_confirmation_input(self, context: ExecutionContext, user_input: str,
                                               workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle input during payment confirmation wait"""
        try:
            # Check for skepticism keywords
            skepticism_keywords = ["scam", "secure", "who are you", "trust", "safe"]
            if any(keyword in user_input.lower() for keyword in skepticism_keywords):
                # Trigger reassurance script
                reassurance_script = context.variables.get("reassurance_script", "")
                if reassurance_script:
                    audio_data = await self.edge_tts_client.synthesize_speech(
                        text=reassurance_script,
                        language="en",
                        voice_settings={"pitch": "-3%", "rate": "-5%"}  # Trustworthy tone
                    )
                    
                    return {
                        "response_text": reassurance_script,
                        "audio_data": audio_data,
                        "continue_waiting": True
                    }
            
            # Continue waiting for SMS confirmation
            return {
                "response_text": "Please complete the payment and I will confirm receipt.",
                "continue_waiting": True
            }
            
        except Exception as e:
            logger.error(f"Error handling payment confirmation input: {e}")
            return {"error": "Failed to handle payment input"}
    
    async def _continue_workflow(self, context: ExecutionContext, user_input: str,
                               workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Continue workflow execution"""
        try:
            # Update context with new input
            context.variables["last_user_input"] = user_input
            
            # Get current node
            current_node = self._find_node_by_id(workflow_data, context.current_node_id)
            if not current_node:
                return await self._create_default_response(context.session_id, user_input)
            
            # Execute current node
            result = await self._execute_node(context, current_node, workflow_data)
            
            return {
                "response_text": result.output_data.get("ai_response", ""),
                "audio_data": result.output_data.get("audio_data"),
                "workflow_state": {
                    "current_node": context.current_node_id,
                    "status": context.status.value,
                    "variables": context.variables
                },
                "actions": self._extract_actions_from_result(result)
            }
            
        except Exception as e:
            logger.error(f"Error continuing workflow: {e}")
            return {"error": "Failed to continue workflow"}
    
    def _extract_actions_from_result(self, result: InvocationResult) -> List[Dict[str, Any]]:
        """Extract actions from invocation result"""
        actions = []
        
        if result.output_data.get("call_ended"):
            actions.append({"type": "hangup"})
        
        if result.output_data.get("sms_sent"):
            actions.append({
                "type": "sms_sent",
                "recipient": result.output_data.get("recipient"),
                "message": result.output_data.get("message")
            })
        
        return actions
    
    async def _create_default_response(self, session_id: int, user_input: str) -> Dict[str, Any]:
        """Create default AI response when no workflow is active"""
        try:
            # Simple AI response without workflow
            prompt_text = f"User said: {user_input}\nRespond helpfully as an AI assistant."
            
            ai_response = await self.gemini_client.generate_response(prompt_text=prompt_text)
            
            if ai_response:
                audio_data = await self.edge_tts_client.synthesize_speech(
                    text=ai_response,
                    language="en"
                )
                
                return {
                    "response_text": ai_response,
                    "audio_data": audio_data
                }
            
            return {"response_text": "I'm here to help. How can I assist you?"}
            
        except Exception as e:
            logger.error(f"Error creating default response: {e}")
            return {"response_text": "I'm sorry, I'm having trouble understanding. Could you please repeat?"}
    
    async def _handle_node_failure(self, context: ExecutionContext, node: Dict[str, Any], 
                                 result: InvocationResult):
        """Handle node execution failure"""
        try:
            logger.error(f"Node {node['id']} failed: {result.error_message}")
            
            # For now, mark workflow as failed
            # Could be enhanced to handle error recovery paths
            context.status = ExecutionStatus.FAILED
            
        except Exception as e:
            logger.error(f"Error handling node failure: {e}")
    
    def get_active_contexts(self) -> Dict[int, ExecutionContext]:
        """Get all active execution contexts"""
        return self.active_contexts.copy()
    
    def get_context(self, session_id: int) -> Optional[ExecutionContext]:
        """Get execution context for session"""
        return self.active_contexts.get(session_id)
    
    def cleanup_context(self, session_id: int):
        """Clean up execution context"""
        if session_id in self.active_contexts:
            del self.active_contexts[session_id]
            logger.info(f"Cleaned up workflow context for session {session_id}")
    
    async def handle_sms_payment_confirmation(self, session_id: int, sms_content: str, 
                                            analysis_result: Dict[str, Any]) -> bool:
        """Handle SMS payment confirmation"""
        try:
            context = self.active_contexts.get(session_id)
            if not context or not context.variables.get("awaiting_payment"):
                return False
            
            if analysis_result.get("status") == "CONFIRMED":
                # Payment confirmed, continue workflow
                context.status = ExecutionStatus.RUNNING
                context.variables["payment_confirmed"] = True
                context.variables["awaiting_payment"] = False
                
                # Continue to next nodes
                workflow = await self._load_workflow(context.workflow_id)
                next_nodes = self._get_connected_nodes(
                    workflow.workflow_data, context.current_node_id
                )
                
                if next_nodes:
                    await self._continue_to_next_nodes(context, next_nodes, workflow.workflow_data)
                else:
                    context.status = ExecutionStatus.COMPLETED
                
                logger.info(f"Payment confirmed for session {session_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error handling SMS payment confirmation: {e}")
            return False