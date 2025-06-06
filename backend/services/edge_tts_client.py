"""
Edge TTS client
The Scribe's Voice Synthesis
"""

import os
import logging
import asyncio
import tempfile
from typing import Optional, Dict, Any
import edge_tts
from io import BytesIO

logger = logging.getLogger(__name__)

class EdgeTTSClient:
    """Client for Microsoft Edge Text-to-Speech service"""
    
    def __init__(self):
        self.voice_mapping = self._initialize_voice_mapping()
        logger.info("🗣️ Edge TTS client initialized")
    
    def _initialize_voice_mapping(self) -> Dict[str, Dict[str, str]]:
        """Initialize language to voice mapping"""
        return {
            "en": {
                "female": "en-US-AriaNeural",
                "male": "en-US-GuyNeural",
                "default": "en-US-AriaNeural"
            },
            "ru": {
                "female": "ru-RU-SvetlanaNeural",
                "male": "ru-RU-DmitryNeural", 
                "default": "ru-RU-SvetlanaNeural"
            },
            "ar": {
                "female": "ar-SA-ZariyahNeural",
                "male": "ar-SA-HamedNeural",
                "default": "ar-SA-ZariyahNeural"
            },
            "zh": {
                "female": "zh-CN-XiaoxiaoNeural",
                "male": "zh-CN-YunxiNeural",
                "default": "zh-CN-XiaoxiaoNeural"
            },
            "es": {
                "female": "es-ES-ElviraNeural",
                "male": "es-ES-AlvaroNeural",
                "default": "es-ES-ElviraNeural"
            },
            "fr": {
                "female": "fr-FR-DeniseNeural",
                "male": "fr-FR-HenriNeural",
                "default": "fr-FR-DeniseNeural"
            },
            "de": {
                "female": "de-DE-KatjaNeural",
                "male": "de-DE-ConradNeural",
                "default": "de-DE-KatjaNeural"
            },
            "it": {
                "female": "it-IT-ElsaNeural",
                "male": "it-IT-DiegoNeural",
                "default": "it-IT-ElsaNeural"
            },
            "ja": {
                "female": "ja-JP-NanamiNeural",
                "male": "ja-JP-KeitaNeural",
                "default": "ja-JP-NanamiNeural"
            },
            "ko": {
                "female": "ko-KR-SunHiNeural",
                "male": "ko-KR-InJoonNeural",
                "default": "ko-KR-SunHiNeural"
            }
        }
    
    async def synthesize_speech(
        self,
        text: str,
        language: str = "en",
        gender: str = "female",
        emotion: str = "neutral",
        speed_adjustment: float = 0.0,
        pitch_adjustment: float = 0.0,
        volume_adjustment: float = 0.0
    ) -> Optional[bytes]:
        """
        Synthesize speech from text with dynamic voice adjustments
        
        Args:
            text: Text to synthesize
            language: Language code (en, ru, ar, etc.)
            gender: Voice gender (female, male)
            emotion: Emotional tone (neutral, calm, excited, concerned)
            speed_adjustment: Speed adjustment (-50% to +50%)
            pitch_adjustment: Pitch adjustment (-50Hz to +50Hz)
            volume_adjustment: Volume adjustment (-50% to +50%)
            
        Returns:
            Audio data as bytes or None if failed
        """
        try:
            # Select appropriate voice
            voice = self._select_voice(language, gender)
            
            # Apply emotional adjustments to speech parameters
            rate, pitch, volume = self._calculate_speech_parameters(
                emotion, speed_adjustment, pitch_adjustment, volume_adjustment
            )
            
            # Create SSML with prosody adjustments
            ssml_text = self._create_ssml(text, voice, rate, pitch, volume)
            
            # Generate speech
            communicate = edge_tts.Communicate(ssml_text, voice)
            
            # Collect audio data
            audio_data = BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data.write(chunk["data"])
            
            audio_bytes = audio_data.getvalue()
            
            if len(audio_bytes) > 0:
                logger.info(f"TTS generated: {len(text)} chars -> {len(audio_bytes)} bytes audio")
                return audio_bytes
            else:
                logger.error("TTS generated empty audio")
                return None
                
        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")
            return None
    
    def _select_voice(self, language: str, gender: str) -> str:
        """Select appropriate voice based on language and gender"""
        lang_voices = self.voice_mapping.get(language, self.voice_mapping["en"])
        return lang_voices.get(gender, lang_voices["default"])
    
    def _calculate_speech_parameters(
        self,
        emotion: str,
        speed_adj: float,
        pitch_adj: float,
        volume_adj: float
    ) -> tuple:
        """Calculate speech parameters based on emotion and adjustments"""
        
        # Base emotional adjustments
        emotion_adjustments = {
            "neutral": {"rate": 0, "pitch": 0, "volume": 0},
            "calm": {"rate": -10, "pitch": -5, "volume": -5},
            "excited": {"rate": 15, "pitch": 10, "volume": 5},
            "concerned": {"rate": -5, "pitch": -10, "volume": 0},
            "confident": {"rate": 5, "pitch": 5, "volume": 5},
            "reassuring": {"rate": -8, "pitch": -3, "volume": 0}
        }
        
        base_adj = emotion_adjustments.get(emotion, emotion_adjustments["neutral"])
        
        # Combine with manual adjustments
        final_rate = max(-50, min(50, base_adj["rate"] + speed_adj))
        final_pitch = max(-50, min(50, base_adj["pitch"] + pitch_adj))
        final_volume = max(-50, min(50, base_adj["volume"] + volume_adj))
        
        # Format for SSML
        rate = f"{final_rate:+.0f}%" if final_rate != 0 else "0%"
        pitch = f"{final_pitch:+.0f}Hz" if final_pitch != 0 else "0Hz"
        volume = f"{final_volume:+.0f}%" if final_volume != 0 else "0%"
        
        return rate, pitch, volume
    
    def _create_ssml(self, text: str, voice: str, rate: str, pitch: str, volume: str) -> str:
        """Create SSML markup for enhanced speech synthesis"""
        
        # Escape XML special characters in text
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        
        ssml = f"""<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
    <voice name="{voice}">
        <prosody rate="{rate}" pitch="{pitch}" volume="{volume}">
            {text}
        </prosody>
    </voice>
</speak>"""
        
        return ssml
    
    async def get_available_voices(self) -> list:
        """Get list of available voices"""
        try:
            voices = await edge_tts.list_voices()
            return [
                {
                    "name": voice["Name"],
                    "display_name": voice["DisplayName"],
                    "language": voice["Locale"],
                    "gender": voice["Gender"]
                }
                for voice in voices
            ]
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return []
    
    def map_sentiment_to_emotion(self, sentiment: str, context: str = "") -> str:
        """
        Map AI-detected sentiment to emotional speech parameters
        
        Args:
            sentiment: Detected sentiment from AI response
            context: Additional context for emotion mapping
            
        Returns:
            Emotion string for TTS adjustment
        """
        sentiment_mapping = {
            "positive": "confident",
            "negative": "concerned", 
            "neutral": "neutral",
            "happy": "excited",
            "sad": "calm",
            "angry": "concerned",
            "fear": "reassuring",
            "surprise": "excited",
            "trust": "confident",
            "anticipation": "excited"
        }
        
        # Check context for specific keywords
        if "payment" in context.lower() or "money" in context.lower():
            if sentiment in ["positive", "confident"]:
                return "reassuring"
            elif sentiment in ["negative", "concerned"]:
                return "calm"
        
        return sentiment_mapping.get(sentiment.lower(), "neutral")
    
    async def synthesize_with_auto_emotion(
        self,
        text: str,
        language: str = "en",
        detected_sentiment: str = "neutral",
        context: str = "",
        gender: str = "female"
    ) -> Optional[bytes]:
        """
        Synthesize speech with automatic emotion detection and adjustment
        
        Args:
            text: Text to synthesize
            language: Language code
            detected_sentiment: AI-detected sentiment
            context: Context for emotion mapping
            gender: Voice gender preference
            
        Returns:
            Audio data as bytes
        """
        emotion = self.map_sentiment_to_emotion(detected_sentiment, context)
        
        return await self.synthesize_speech(
            text=text,
            language=language,
            gender=gender,
            emotion=emotion
        )