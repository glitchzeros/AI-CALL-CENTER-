"""
Gemini API client
The Scribe's Mind Interface
"""

import os
import logging
import base64
import json
from typing import Optional, Dict, Any, List
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for interacting with Gemini 2.0 Flash API"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Configure the API
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            }
        )
        
        logger.info("🧠 Gemini client initialized")
    
    async def generate_multimodal_response(
        self,
        prompt_text: str,
        audio_data: Optional[bytes] = None,
        audio_mime_type: str = "audio/wav",
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_output_tokens: int = 2048
    ) -> Dict[str, Any]:
        """
        Generate response from multimodal input (text + audio)
        
        Args:
            prompt_text: The text prompt including conversation history
            audio_data: Raw audio bytes (optional)
            audio_mime_type: MIME type of audio data
            system_instruction: System-level instructions for the AI
            temperature: Creativity level (0.0 to 1.0)
            max_output_tokens: Maximum response length
            
        Returns:
            Dict containing response text, detected language, and metadata
        """
        try:
            # Prepare content parts
            content_parts = [prompt_text]
            
            # Add audio if provided
            if audio_data:
                # Convert audio to base64 for inline transmission
                audio_b64 = base64.b64encode(audio_data).decode()
                content_parts.append({
                    "inline_data": {
                        "mime_type": audio_mime_type,
                        "data": audio_b64
                    }
                })
            
            # Configure generation parameters
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_output_tokens,
                top_p=0.95,
                top_k=40
            )
            
            # Set system instruction if provided
            if system_instruction:
                self.model = genai.GenerativeModel(
                    model_name="gemini-2.0-flash-exp",
                    system_instruction=system_instruction,
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    }
                )
            
            # Generate response
            response = self.model.generate_content(
                content_parts,
                generation_config=generation_config
            )
            
            # Extract response text
            response_text = response.text if response.text else ""
            
            # Parse metadata from response
            metadata = {
                "model_used": "gemini-2.0-flash-exp",
                "finish_reason": getattr(response.candidates[0], 'finish_reason', None) if response.candidates else None,
                "safety_ratings": [
                    {
                        "category": rating.category.name,
                        "probability": rating.probability.name
                    }
                    for rating in getattr(response.candidates[0], 'safety_ratings', [])
                ] if response.candidates else [],
                "usage_metadata": {
                    "prompt_token_count": getattr(response, 'usage_metadata', {}).get('prompt_token_count', 0),
                    "candidates_token_count": getattr(response, 'usage_metadata', {}).get('candidates_token_count', 0),
                    "total_token_count": getattr(response, 'usage_metadata', {}).get('total_token_count', 0)
                }
            }
            
            # Attempt to detect language from response
            detected_language = self._detect_language_from_response(response_text)
            
            logger.info(f"Gemini response generated: {len(response_text)} chars, language: {detected_language}")
            
            return {
                "response_text": response_text,
                "detected_language": detected_language,
                "metadata": metadata,
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return {
                "response_text": "",
                "detected_language": "unknown",
                "metadata": {"error": str(e)},
                "success": False,
                "error": str(e)
            }
    
    async def analyze_conversation_for_summary(
        self,
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """
        Generate AI summary of conversation
        
        Args:
            conversation_history: List of messages with speaker and content
            
        Returns:
            Generated summary text
        """
        try:
            # Format conversation for analysis
            conversation_text = "\n".join([
                f"{msg['speaker']}: {msg['content']}"
                for msg in conversation_history
            ])
            
            prompt = f"""Summarize the key points, user intent, and outcome of the following conversation between a user and an AI agent. Keep the summary under 200 words and focus on:
1. What the user wanted
2. What actions were taken
3. The final outcome
4. Any important details or issues

Conversation:
{conversation_text}

Summary:"""
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,
                    max_output_tokens=300
                )
            )
            
            summary = response.text if response.text else "Summary generation failed"
            logger.info(f"Conversation summary generated: {len(summary)} chars")
            
            return summary
            
        except Exception as e:
            logger.error(f"Summary generation error: {e}")
            return f"Summary generation failed: {str(e)}"
    
    async def analyze_sms_for_payment_confirmation(
        self,
        sms_content: str,
        conversation_context: str
    ) -> str:
        """
        Analyze SMS content to determine if it confirms payment
        
        Args:
            sms_content: The SMS message content
            conversation_context: Previous conversation context
            
        Returns:
            One of: 'CONFIRMED', 'REJECTED', 'IRRELEVANT'
        """
        try:
            prompt = f"""Analyze the following SMS in the context of the preceding conversation. Does it confirm a successful payment transaction related to the user's intent to pay? 

Context:
{conversation_context}

SMS Content:
{sms_content}

Respond ONLY with one of these exact words: 'CONFIRMED', 'REJECTED', or 'IRRELEVANT'"""
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=10
                )
            )
            
            result = response.text.strip().upper() if response.text else "IRRELEVANT"
            
            # Ensure valid response
            if result not in ["CONFIRMED", "REJECTED", "IRRELEVANT"]:
                result = "IRRELEVANT"
            
            logger.info(f"SMS payment analysis: {result}")
            return result
            
        except Exception as e:
            logger.error(f"SMS analysis error: {e}")
            return "IRRELEVANT"
    
    async def analyze_conversations_for_insights(
        self,
        anonymized_conversations: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Analyze anonymized conversations for meta-insights (Dream Journal)
        
        Args:
            anonymized_conversations: List of anonymized conversation texts
            
        Returns:
            List of insights with categories and summaries
        """
        try:
            # Combine conversations for analysis
            combined_text = "\n\n---\n\n".join(anonymized_conversations)
            
            prompt = f"""Analyze these anonymized conversation logs between AI Scribes and users. Identify patterns in user behavior, common points of confusion or success related to workflow steps, recurring unhandled requests, or potential areas for Scribe improvement. Generate insights and observations.

Format your response as JSON with this structure:
{{
  "insights": [
    {{
      "category": "workflow_friction|potential_feature|performance_observation|sentiment_analysis|data_anomaly",
      "summary": "Brief description of the insight",
      "severity": "low|medium|high",
      "related_invocations": ["list", "of", "relevant", "invocation", "types"],
      "example_snippet": "very short anonymized example if applicable"
    }}
  ]
}}

Conversations:
{combined_text}"""
            
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.4,
                    max_output_tokens=2048
                )
            )
            
            # Parse JSON response
            try:
                insights_data = json.loads(response.text)
                insights = insights_data.get("insights", [])
                logger.info(f"Generated {len(insights)} insights from {len(anonymized_conversations)} conversations")
                return insights
            except json.JSONDecodeError:
                logger.error("Failed to parse insights JSON response")
                return []
            
        except Exception as e:
            logger.error(f"Insights analysis error: {e}")
            return []
    
    def _detect_language_from_response(self, text: str) -> str:
        """
        Simple language detection from response text
        """
        # Basic language detection based on character patterns
        # This is a simplified approach - in production, you might use a proper language detection library
        
        if not text:
            return "unknown"
        
        # Check for common language patterns
        cyrillic_chars = sum(1 for c in text if '\u0400' <= c <= '\u04FF')
        arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        
        total_chars = len([c for c in text if c.isalpha()])
        
        if total_chars == 0:
            return "unknown"
        
        # Determine language based on character distribution
        if cyrillic_chars / total_chars > 0.3:
            return "ru"
        elif arabic_chars / total_chars > 0.3:
            return "ar"
        elif chinese_chars / total_chars > 0.3:
            return "zh"
        else:
            return "en"  # Default to English
    
    async def generate_text_response(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7
    ) -> str:
        """
        Generate a simple text response from a text prompt
        Used for support chat and other text-only interactions
        
        Args:
            prompt: The text prompt
            max_tokens: Maximum response length
            temperature: Creativity level (0.0 to 1.0)
            
        Returns:
            Generated response text
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    top_p=0.95,
                    top_k=40
                )
            )
            
            response_text = response.text if response.text else ""
            logger.info(f"Text response generated: {len(response_text)} chars")
            
            return response_text
            
        except Exception as e:
            logger.error(f"Text generation error: {e}")
            return ""
    
    async def count_tokens(self, text: str) -> int:
        """
        Count tokens in text for context management
        """
        try:
            response = self.model.count_tokens(text)
            return response.total_tokens
        except Exception as e:
            logger.error(f"Token counting error: {e}")
            # Fallback estimation: roughly 4 characters per token
            return len(text) // 4