"""
Audio Processing Pipeline
The Scribe's Voice Enhancement System
"""

import asyncio
import logging
import numpy as np
import librosa
import soundfile as sf
import webrtcvad
import noisereduce as nr
from scipy import signal
import pyaudio
import threading
import queue
import time
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger("aetherium.audio")

@dataclass
class AudioConfig:
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024
    format: int = pyaudio.paInt16
    vad_aggressiveness: int = 2  # 0-3, higher = more aggressive
    noise_reduction_strength: float = 0.8

class AudioProcessor:
    """Advanced audio processing pipeline for voice enhancement"""
    
    def __init__(self, config: AudioConfig = None):
        self.config = config or AudioConfig()
        self.vad = None
        self.audio_interface = None
        self.processing_queue = queue.Queue()
        self.output_queue = queue.Queue()
        self.is_running = False
        self.processing_thread = None
        
        # Audio buffers
        self.input_buffer = []
        self.output_buffer = []
        
        # Processing statistics
        self.stats = {
            'frames_processed': 0,
            'voice_frames': 0,
            'noise_frames': 0,
            'processing_time_ms': 0
        }
        
    async def initialize(self):
        """Initialize audio processing components"""
        logger.info("🎵 Initializing audio processor...")
        
        try:
            # Initialize WebRTC VAD
            self.vad = webrtcvad.Vad(self.config.vad_aggressiveness)
            
            # Initialize PyAudio
            self.audio_interface = pyaudio.PyAudio()
            
            # Start processing thread
            self.is_running = True
            self.processing_thread = threading.Thread(target=self._processing_loop, daemon=True)
            self.processing_thread.start()
            
            logger.info("✅ Audio processor initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize audio processor: {e}")
            raise
    
    def _processing_loop(self):
        """Main audio processing loop"""
        logger.info("🔄 Audio processing loop started")
        
        while self.is_running:
            try:
                # Get audio chunk from queue (blocking with timeout)
                try:
                    audio_data, metadata = self.processing_queue.get(timeout=0.1)
                except queue.Empty:
                    continue
                
                # Process the audio chunk
                processed_audio, processing_metadata = self._process_audio_chunk(audio_data, metadata)
                
                # Put processed audio in output queue
                self.output_queue.put((processed_audio, processing_metadata))
                
                # Update statistics
                self.stats['frames_processed'] += 1
                
            except Exception as e:
                logger.error(f"Error in audio processing loop: {e}")
                time.sleep(0.01)
        
        logger.info("🔄 Audio processing loop stopped")
    
    def _process_audio_chunk(self, audio_data: bytes, metadata: Dict[str, Any]) -> Tuple[bytes, Dict[str, Any]]:
        """Process a single audio chunk"""
        start_time = time.time()
        
        try:
            # Convert bytes to numpy array
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            
            # Ensure correct sample rate
            if metadata.get('sample_rate', self.config.sample_rate) != self.config.sample_rate:
                audio_array = self._resample_audio(audio_array, metadata.get('sample_rate'), self.config.sample_rate)
            
            # Voice Activity Detection
            is_voice = self._detect_voice_activity(audio_data)
            
            # Apply noise reduction if voice is detected
            if is_voice:
                audio_array = self._apply_noise_reduction(audio_array)
                self.stats['voice_frames'] += 1
            else:
                self.stats['noise_frames'] += 1
            
            # Apply audio enhancement
            audio_array = self._enhance_audio(audio_array)
            
            # Convert back to bytes
            processed_audio = audio_array.astype(np.int16).tobytes()
            
            # Update metadata
            processing_metadata = {
                **metadata,
                'is_voice': is_voice,
                'processing_time_ms': (time.time() - start_time) * 1000,
                'sample_rate': self.config.sample_rate,
                'channels': self.config.channels
            }
            
            self.stats['processing_time_ms'] += processing_metadata['processing_time_ms']
            
            return processed_audio, processing_metadata
            
        except Exception as e:
            logger.error(f"Error processing audio chunk: {e}")
            return audio_data, metadata
    
    def _detect_voice_activity(self, audio_data: bytes) -> bool:
        """Detect voice activity using WebRTC VAD"""
        try:
            # VAD requires specific frame sizes (10, 20, or 30 ms)
            frame_duration_ms = 30
            frame_size = int(self.config.sample_rate * frame_duration_ms / 1000)
            
            # Ensure audio data is the right size
            if len(audio_data) < frame_size * 2:  # 2 bytes per sample for int16
                return False
            
            # Take the first frame of the required size
            frame_data = audio_data[:frame_size * 2]
            
            # Check if frame contains voice
            return self.vad.is_speech(frame_data, self.config.sample_rate)
            
        except Exception as e:
            logger.debug(f"VAD error: {e}")
            return True  # Default to voice if VAD fails
    
    def _apply_noise_reduction(self, audio_array: np.ndarray) -> np.ndarray:
        """Apply noise reduction to audio"""
        try:
            # Convert to float for processing
            audio_float = audio_array.astype(np.float32) / 32768.0
            
            # Apply noise reduction
            reduced_noise = nr.reduce_noise(
                y=audio_float,
                sr=self.config.sample_rate,
                prop_decrease=self.config.noise_reduction_strength
            )
            
            # Convert back to int16 range
            return (reduced_noise * 32768.0).astype(np.int16)
            
        except Exception as e:
            logger.debug(f"Noise reduction error: {e}")
            return audio_array
    
    def _enhance_audio(self, audio_array: np.ndarray) -> np.ndarray:
        """Apply audio enhancement (AGC, equalization)"""
        try:
            # Convert to float for processing
            audio_float = audio_array.astype(np.float32) / 32768.0
            
            # Automatic Gain Control (AGC)
            audio_float = self._apply_agc(audio_float)
            
            # Basic equalization (boost speech frequencies)
            audio_float = self._apply_equalization(audio_float)
            
            # Convert back to int16 range
            enhanced = (audio_float * 32768.0).astype(np.int16)
            
            # Ensure no clipping
            enhanced = np.clip(enhanced, -32768, 32767)
            
            return enhanced
            
        except Exception as e:
            logger.debug(f"Audio enhancement error: {e}")
            return audio_array
    
    def _apply_agc(self, audio: np.ndarray, target_level: float = 0.3) -> np.ndarray:
        """Apply Automatic Gain Control"""
        try:
            # Calculate RMS level
            rms = np.sqrt(np.mean(audio ** 2))
            
            if rms > 0:
                # Calculate gain needed to reach target level
                gain = target_level / rms
                
                # Limit gain to prevent excessive amplification
                gain = min(gain, 4.0)  # Max 4x amplification
                
                return audio * gain
            
            return audio
            
        except Exception as e:
            logger.debug(f"AGC error: {e}")
            return audio
    
    def _apply_equalization(self, audio: np.ndarray) -> np.ndarray:
        """Apply basic equalization to enhance speech frequencies"""
        try:
            # Design a simple bandpass filter for speech frequencies (300-3400 Hz)
            nyquist = self.config.sample_rate / 2
            low_freq = 300 / nyquist
            high_freq = 3400 / nyquist
            
            # Create bandpass filter
            b, a = signal.butter(4, [low_freq, high_freq], btype='band')
            
            # Apply filter
            filtered = signal.filtfilt(b, a, audio)
            
            # Mix with original (50% filtered, 50% original)
            return 0.5 * audio + 0.5 * filtered
            
        except Exception as e:
            logger.debug(f"Equalization error: {e}")
            return audio
    
    def _resample_audio(self, audio: np.ndarray, original_sr: int, target_sr: int) -> np.ndarray:
        """Resample audio to target sample rate"""
        try:
            # Convert to float for resampling
            audio_float = audio.astype(np.float32) / 32768.0
            
            # Resample using librosa
            resampled = librosa.resample(audio_float, orig_sr=original_sr, target_sr=target_sr)
            
            # Convert back to int16 range
            return (resampled * 32768.0).astype(np.int16)
            
        except Exception as e:
            logger.error(f"Resampling error: {e}")
            return audio
    
    async def process_audio_stream(self, audio_data: bytes, metadata: Dict[str, Any] = None) -> Optional[Tuple[bytes, Dict[str, Any]]]:
        """Process audio stream asynchronously"""
        if not self.is_running:
            return None
        
        # Add to processing queue
        self.processing_queue.put((audio_data, metadata or {}))
        
        # Try to get processed result (non-blocking)
        try:
            return self.output_queue.get_nowait()
        except queue.Empty:
            return None
    
    def process_audio_file(self, input_path: str, output_path: str) -> bool:
        """Process an audio file"""
        try:
            # Load audio file
            audio_data, sample_rate = librosa.load(input_path, sr=self.config.sample_rate, mono=True)
            
            # Convert to int16
            audio_int16 = (audio_data * 32768.0).astype(np.int16)
            
            # Process in chunks
            chunk_size = self.config.chunk_size
            processed_chunks = []
            
            for i in range(0, len(audio_int16), chunk_size):
                chunk = audio_int16[i:i + chunk_size]
                chunk_bytes = chunk.tobytes()
                
                # Process chunk
                processed_bytes, _ = self._process_audio_chunk(chunk_bytes, {'sample_rate': sample_rate})
                processed_chunk = np.frombuffer(processed_bytes, dtype=np.int16)
                processed_chunks.append(processed_chunk)
            
            # Combine processed chunks
            processed_audio = np.concatenate(processed_chunks)
            
            # Convert to float for saving
            processed_float = processed_audio.astype(np.float32) / 32768.0
            
            # Save processed audio
            sf.write(output_path, processed_float, self.config.sample_rate)
            
            logger.info(f"Processed audio file: {input_path} -> {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing audio file: {e}")
            return False
    
    def get_available_devices(self) -> Dict[str, Any]:
        """Get available audio input/output devices"""
        if not self.audio_interface:
            return {}
        
        try:
            device_info = {
                'input_devices': [],
                'output_devices': [],
                'default_input': None,
                'default_output': None
            }
            
            # Get default devices
            try:
                device_info['default_input'] = self.audio_interface.get_default_input_device_info()
            except:
                pass
            
            try:
                device_info['default_output'] = self.audio_interface.get_default_output_device_info()
            except:
                pass
            
            # Get all devices
            for i in range(self.audio_interface.get_device_count()):
                try:
                    info = self.audio_interface.get_device_info_by_index(i)
                    
                    if info['maxInputChannels'] > 0:
                        device_info['input_devices'].append({
                            'index': i,
                            'name': info['name'],
                            'channels': info['maxInputChannels'],
                            'sample_rate': info['defaultSampleRate']
                        })
                    
                    if info['maxOutputChannels'] > 0:
                        device_info['output_devices'].append({
                            'index': i,
                            'name': info['name'],
                            'channels': info['maxOutputChannels'],
                            'sample_rate': info['defaultSampleRate']
                        })
                        
                except Exception as e:
                    logger.debug(f"Error getting device {i}: {e}")
                    continue
            
            return device_info
            
        except Exception as e:
            logger.error(f"Error getting audio devices: {e}")
            return {}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return {
            **self.stats,
            'queue_size': self.processing_queue.qsize(),
            'output_queue_size': self.output_queue.qsize(),
            'is_running': self.is_running,
            'avg_processing_time_ms': (
                self.stats['processing_time_ms'] / max(1, self.stats['frames_processed'])
            )
        }
    
    def reset_statistics(self):
        """Reset processing statistics"""
        self.stats = {
            'frames_processed': 0,
            'voice_frames': 0,
            'noise_frames': 0,
            'processing_time_ms': 0
        }
    
    async def cleanup(self):
        """Cleanup audio processor"""
        logger.info("🧹 Cleaning up audio processor...")
        
        self.is_running = False
        
        if self.processing_thread and self.processing_thread.is_alive():
            self.processing_thread.join(timeout=2.0)
        
        if self.audio_interface:
            self.audio_interface.terminate()
            self.audio_interface = None
        
        # Clear queues
        while not self.processing_queue.empty():
            try:
                self.processing_queue.get_nowait()
            except queue.Empty:
                break
        
        while not self.output_queue.empty():
            try:
                self.output_queue.get_nowait()
            except queue.Empty:
                break
        
        logger.info("🧹 Audio processor cleanup complete")