"""
Device Manager
Handles USB device detection and mapping for GSM modems
"""

import asyncio
import logging
import os
import glob
import re
from typing import Dict, List, Tuple, Optional
import serial.tools.list_ports

logger = logging.getLogger("aetherium.modems")

class DeviceManager:
    """Manages USB device detection and mapping for dual-port GSM modems"""
    
    def __init__(self):
        self.usb_devices = {}
        self.audio_devices = {}
        self.modem_pairs = {}  # Maps device_id to (control_port, audio_port)
        
    async def initialize(self):
        """Initialize device detection"""
        logger.info("🔍 Initializing device detection...")
        await self.scan_devices()
        await self.map_modem_pairs()
        logger.info(f"✅ Device detection complete: {len(self.modem_pairs)} modem pairs found")
    
    async def scan_devices(self):
        """Scan for USB serial devices and audio devices"""
        # Scan USB serial ports
        await self.scan_usb_serial_devices()
        
        # Scan audio devices
        await self.scan_audio_devices()
    
    async def scan_usb_serial_devices(self):
        """Scan for USB serial devices (ttyUSB*)"""
        try:
            ports = serial.tools.list_ports.comports()
            usb_ports = []
            
            for port in ports:
                if 'ttyUSB' in port.device or 'ttyACM' in port.device:
                    usb_ports.append({
                        'device': port.device,
                        'description': port.description,
                        'hwid': port.hwid,
                        'vid': port.vid,
                        'pid': port.pid,
                        'serial_number': port.serial_number,
                        'location': port.location
                    })
            
            # Group by USB location/serial to identify modem pairs
            self.usb_devices = {}
            for port in usb_ports:
                # Extract USB bus and device info from location
                location_key = self._extract_location_key(port)
                if location_key not in self.usb_devices:
                    self.usb_devices[location_key] = []
                self.usb_devices[location_key].append(port)
            
            logger.info(f"Found {len(usb_ports)} USB serial devices in {len(self.usb_devices)} groups")
            
        except Exception as e:
            logger.error(f"Error scanning USB devices: {e}")
    
    async def scan_audio_devices(self):
        """Scan for audio devices (ALSA PCM devices)"""
        try:
            # Look for ALSA PCM devices
            pcm_devices = glob.glob('/dev/snd/pcmC*D*p')  # Playback devices
            pcm_capture = glob.glob('/dev/snd/pcmC*D*c')  # Capture devices
            
            self.audio_devices = {}
            
            # Parse PCM device names to extract card and device numbers
            for device_path in pcm_devices + pcm_capture:
                match = re.search(r'pcmC(\d+)D(\d+)([pc])', device_path)
                if match:
                    card_num = int(match.group(1))
                    device_num = int(match.group(2))
                    device_type = 'playback' if match.group(3) == 'p' else 'capture'
                    
                    key = f"card{card_num}_device{device_num}"
                    if key not in self.audio_devices:
                        self.audio_devices[key] = {
                            'card': card_num,
                            'device': device_num,
                            'playback': None,
                            'capture': None
                        }
                    
                    self.audio_devices[key][device_type] = device_path
            
            logger.info(f"Found {len(self.audio_devices)} audio device groups")
            
        except Exception as e:
            logger.error(f"Error scanning audio devices: {e}")
    
    async def map_modem_pairs(self):
        """Map USB serial ports to audio devices for each modem"""
        try:
            self.modem_pairs = {}
            
            # For each USB device group, try to find corresponding audio device
            for location_key, usb_ports in self.usb_devices.items():
                if len(usb_ports) >= 2:  # Need at least 2 ports for control + audio
                    # Sort ports by device name to get consistent ordering
                    sorted_ports = sorted(usb_ports, key=lambda x: x['device'])
                    
                    # Assign first port as control, second as audio interface
                    control_port = sorted_ports[0]['device']
                    
                    # Try to find corresponding audio device
                    audio_port = await self._find_audio_device_for_usb(location_key)
                    
                    if audio_port:
                        device_id = f"modem_{location_key}"
                        self.modem_pairs[device_id] = {
                            'control_port': control_port,
                            'audio_port': audio_port,
                            'usb_location': location_key,
                            'usb_ports': sorted_ports
                        }
                        
                        logger.info(f"Mapped modem {device_id}: control={control_port}, audio={audio_port}")
                    else:
                        logger.warning(f"No audio device found for USB group {location_key}")
                else:
                    logger.warning(f"USB group {location_key} has only {len(usb_ports)} ports (need 2)")
            
        except Exception as e:
            logger.error(f"Error mapping modem pairs: {e}")
    
    def _extract_location_key(self, port_info: dict) -> str:
        """Extract a unique location key from USB port info"""
        # Use USB location if available
        if port_info.get('location'):
            # Extract bus and port info from location string
            location = port_info['location']
            # Format: "1-1.4:1.0" -> extract "1-1.4"
            if ':' in location:
                bus_port = location.split(':')[0]
                return bus_port
        
        # Fallback to serial number or VID:PID
        if port_info.get('serial_number'):
            return f"sn_{port_info['serial_number']}"
        
        if port_info.get('vid') and port_info.get('pid'):
            return f"vid{port_info['vid']:04x}_pid{port_info['pid']:04x}"
        
        # Last resort: use device name prefix
        device = port_info['device']
        if 'ttyUSB' in device:
            # Extract base number: /dev/ttyUSB0 -> ttyUSB0
            base = device.split('/')[-1]
            # Group by pairs: ttyUSB0,ttyUSB1 -> ttyUSB0
            num = int(re.search(r'(\d+)$', base).group(1))
            return f"ttyUSB{num // 2 * 2}"
        
        return device
    
    async def _find_audio_device_for_usb(self, usb_location: str) -> Optional[str]:
        """Find corresponding audio device for USB location"""
        # This is a simplified mapping - in production, you'd need more sophisticated
        # device correlation based on USB topology or device-specific identifiers
        
        # For now, assign audio devices in order
        audio_keys = list(self.audio_devices.keys())
        modem_index = len(self.modem_pairs)
        
        if modem_index < len(audio_keys):
            audio_key = audio_keys[modem_index]
            audio_info = self.audio_devices[audio_key]
            
            # Return the card:device format used by ALSA
            return f"hw:{audio_info['card']},{audio_info['device']}"
        
        return None
    
    def get_modem_pairs(self) -> Dict[str, Dict]:
        """Get all detected modem pairs"""
        return self.modem_pairs.copy()
    
    def get_modem_pair(self, device_id: str) -> Optional[Dict]:
        """Get specific modem pair by device ID"""
        return self.modem_pairs.get(device_id)
    
    async def refresh_devices(self):
        """Refresh device detection"""
        logger.info("🔄 Refreshing device detection...")
        await self.scan_devices()
        await self.map_modem_pairs()
        logger.info("✅ Device refresh complete")
    
    async def cleanup(self):
        """Cleanup device manager"""
        logger.info("🧹 Device manager cleanup")
        self.usb_devices.clear()
        self.audio_devices.clear()
        self.modem_pairs.clear()