"""
Modem Controller
Manages GSM modem communication via AT commands
"""

import asyncio
import logging
import serial
import time
from typing import Dict, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger("aetherium.modems")

class ModemStatus(Enum):
    OFFLINE = "offline"
    INITIALIZING = "initializing"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"

@dataclass
class ModemInfo:
    device_id: str
    control_port: str
    audio_port: str
    phone_number: Optional[str] = None
    status: ModemStatus = ModemStatus.OFFLINE
    signal_strength: int = 0
    serial_connection: Optional[serial.Serial] = None
    last_seen: float = 0
    network_registered: bool = False

class ModemController:
    """Controls GSM modems via AT commands"""
    
    def __init__(self, device_manager):
        self.device_manager = device_manager
        self.modems: Dict[str, ModemInfo] = {}
        self.command_lock = asyncio.Lock()
        self.monitoring_task = None
        
    async def initialize(self):
        """Initialize all detected modems"""
        logger.info("📡 Initializing modem controller...")
        
        modem_pairs = self.device_manager.get_modem_pairs()
        
        for device_id, pair_info in modem_pairs.items():
            try:
                modem = ModemInfo(
                    device_id=device_id,
                    control_port=pair_info['control_port'],
                    audio_port=pair_info['audio_port']
                )
                
                # Initialize modem connection
                if await self._initialize_modem(modem):
                    self.modems[device_id] = modem
                    logger.info(f"✅ Modem {device_id} initialized successfully")
                else:
                    logger.error(f"❌ Failed to initialize modem {device_id}")
                    
            except Exception as e:
                logger.error(f"Error initializing modem {device_id}: {e}")
        
        # Start monitoring task
        self.monitoring_task = asyncio.create_task(self._monitor_modems())
        
        logger.info(f"📡 Modem controller ready: {len(self.modems)} modems active")
    
    async def _initialize_modem(self, modem: ModemInfo) -> bool:
        """Initialize a single modem"""
        try:
            # Open serial connection
            modem.serial_connection = serial.Serial(
                port=modem.control_port,
                baudrate=115200,
                timeout=5,
                write_timeout=5
            )
            
            modem.status = ModemStatus.INITIALIZING
            
            # Send basic AT commands to initialize modem
            commands = [
                "ATZ",          # Reset modem
                "ATE0",         # Disable echo
                "AT+CMEE=1",    # Enable error reporting
                "AT+CREG=1",    # Enable network registration notifications
                "AT+CLIP=1",    # Enable caller ID
                "AT+CMGF=1",    # Set SMS text mode
                "AT+CNMI=2,2,0,0,0",  # SMS notification settings
            ]
            
            for cmd in commands:
                if not await self._send_at_command(modem, cmd):
                    logger.error(f"Failed to send command {cmd} to {modem.device_id}")
                    return False
                await asyncio.sleep(0.1)
            
            # Get modem info
            await self._update_modem_info(modem)
            
            modem.status = ModemStatus.IDLE
            modem.last_seen = time.time()
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing modem {modem.device_id}: {e}")
            if modem.serial_connection:
                modem.serial_connection.close()
                modem.serial_connection = None
            modem.status = ModemStatus.ERROR
            return False
    
    async def _send_at_command(self, modem: ModemInfo, command: str, timeout: float = 5.0) -> Optional[str]:
        """Send AT command to modem and get response"""
        if not modem.serial_connection or not modem.serial_connection.is_open:
            return None
        
        try:
            # Clear input buffer
            modem.serial_connection.reset_input_buffer()
            
            # Send command
            cmd_bytes = f"{command}\r\n".encode('utf-8')
            modem.serial_connection.write(cmd_bytes)
            
            # Read response
            response_lines = []
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if modem.serial_connection.in_waiting > 0:
                    line = modem.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        response_lines.append(line)
                        
                        # Check for command completion
                        if line in ['OK', 'ERROR'] or line.startswith('+CME ERROR') or line.startswith('+CMS ERROR'):
                            break
                else:
                    await asyncio.sleep(0.01)
            
            response = '\n'.join(response_lines)
            
            # Log command and response for debugging
            logger.debug(f"Modem {modem.device_id}: {command} -> {response}")
            
            return response
            
        except Exception as e:
            logger.error(f"Error sending AT command to {modem.device_id}: {e}")
            return None
    
    async def _update_modem_info(self, modem: ModemInfo):
        """Update modem information"""
        try:
            # Get signal strength
            response = await self._send_at_command(modem, "AT+CSQ")
            if response and "+CSQ:" in response:
                try:
                    csq_line = [line for line in response.split('\n') if '+CSQ:' in line][0]
                    rssi = int(csq_line.split(':')[1].split(',')[0].strip())
                    if rssi != 99:  # 99 means unknown
                        modem.signal_strength = rssi
                except:
                    pass
            
            # Check network registration
            response = await self._send_at_command(modem, "AT+CREG?")
            if response and "+CREG:" in response:
                try:
                    creg_line = [line for line in response.split('\n') if '+CREG:' in line][0]
                    status = int(creg_line.split(',')[1].strip())
                    modem.network_registered = status in [1, 5]  # 1=home, 5=roaming
                except:
                    pass
            
            # Get phone number (if available)
            if not modem.phone_number:
                response = await self._send_at_command(modem, "AT+CNUM")
                if response and "+CNUM:" in response:
                    try:
                        cnum_line = [line for line in response.split('\n') if '+CNUM:' in line][0]
                        # Parse phone number from response
                        parts = cnum_line.split(',')
                        if len(parts) >= 2:
                            phone_num = parts[1].strip().strip('"')
                            if phone_num:
                                modem.phone_number = phone_num
                    except:
                        pass
            
            modem.last_seen = time.time()
            
        except Exception as e:
            logger.error(f"Error updating modem info for {modem.device_id}: {e}")
    
    async def _monitor_modems(self):
        """Monitor modem status and handle incoming events"""
        logger.info("🔍 Starting modem monitoring...")
        
        while True:
            try:
                for modem in self.modems.values():
                    if modem.status == ModemStatus.ERROR:
                        continue
                    
                    # Check for incoming data
                    await self._check_incoming_data(modem)
                    
                    # Update modem info periodically
                    if time.time() - modem.last_seen > 30:  # Every 30 seconds
                        await self._update_modem_info(modem)
                
                await asyncio.sleep(1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in modem monitoring: {e}")
                await asyncio.sleep(5)
        
        logger.info("🔍 Modem monitoring stopped")
    
    async def _check_incoming_data(self, modem: ModemInfo):
        """Check for incoming calls, SMS, and other notifications"""
        if not modem.serial_connection or not modem.serial_connection.is_open:
            return
        
        try:
            if modem.serial_connection.in_waiting > 0:
                line = modem.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    await self._handle_unsolicited_response(modem, line)
                    
        except Exception as e:
            logger.error(f"Error checking incoming data for {modem.device_id}: {e}")
    
    async def _handle_unsolicited_response(self, modem: ModemInfo, response: str):
        """Handle unsolicited responses from modem"""
        try:
            if "RING" in response:
                # Incoming call
                logger.info(f"📞 Incoming call on {modem.device_id}")
                await self._handle_incoming_call(modem)
                
            elif "+CLIP:" in response:
                # Caller ID information
                logger.info(f"📞 Caller ID on {modem.device_id}: {response}")
                
            elif "+CMTI:" in response:
                # New SMS message
                logger.info(f"📱 New SMS on {modem.device_id}: {response}")
                await self._handle_incoming_sms(modem, response)
                
            elif "+CREG:" in response:
                # Network registration status change
                logger.info(f"📡 Network status change on {modem.device_id}: {response}")
                
        except Exception as e:
            logger.error(f"Error handling unsolicited response: {e}")
    
    async def _handle_incoming_call(self, modem: ModemInfo):
        """Handle incoming call"""
        # This will be implemented by the call handler
        # For now, just log the event
        logger.info(f"Incoming call detected on {modem.device_id}")
    
    async def _handle_incoming_sms(self, modem: ModemInfo, notification: str):
        """Handle incoming SMS"""
        # This will be implemented by the SMS handler
        # For now, just log the event
        logger.info(f"Incoming SMS detected on {modem.device_id}: {notification}")
    
    async def send_sms(self, device_id: str, to_number: str, message: str) -> bool:
        """Send SMS via specific modem"""
        modem = self.modems.get(device_id)
        if not modem or modem.status != ModemStatus.IDLE:
            return False
        
        async with self.command_lock:
            try:
                modem.status = ModemStatus.BUSY
                
                # Set SMS text mode
                await self._send_at_command(modem, "AT+CMGF=1")
                
                # Send SMS command
                cmd = f'AT+CMGS="{to_number}"'
                response = await self._send_at_command(modem, cmd, timeout=10)
                
                if response and ">" in response:
                    # Send message content followed by Ctrl+Z
                    message_bytes = f"{message}\x1A".encode('utf-8')
                    modem.serial_connection.write(message_bytes)
                    
                    # Wait for response
                    final_response = await self._read_response(modem, timeout=30)
                    success = final_response and "OK" in final_response
                    
                    logger.info(f"SMS sent from {device_id} to {to_number}: {'success' if success else 'failed'}")
                    return success
                
                return False
                
            except Exception as e:
                logger.error(f"Error sending SMS from {device_id}: {e}")
                return False
            finally:
                modem.status = ModemStatus.IDLE
    
    async def _read_response(self, modem: ModemInfo, timeout: float = 5.0) -> Optional[str]:
        """Read response from modem"""
        try:
            response_lines = []
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                if modem.serial_connection.in_waiting > 0:
                    line = modem.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                    if line:
                        response_lines.append(line)
                        if line in ['OK', 'ERROR'] or line.startswith('+CME ERROR') or line.startswith('+CMS ERROR'):
                            break
                else:
                    await asyncio.sleep(0.01)
            
            return '\n'.join(response_lines)
            
        except Exception as e:
            logger.error(f"Error reading response: {e}")
            return None
    
    async def dial_number(self, device_id: str, number: str) -> bool:
        """Dial a number"""
        modem = self.modems.get(device_id)
        if not modem or modem.status != ModemStatus.IDLE:
            return False
        
        async with self.command_lock:
            try:
                modem.status = ModemStatus.BUSY
                
                # Dial the number
                cmd = f"ATD{number};"
                response = await self._send_at_command(modem, cmd, timeout=30)
                
                success = response and "OK" in response
                logger.info(f"Dial {number} from {device_id}: {'success' if success else 'failed'}")
                
                return success
                
            except Exception as e:
                logger.error(f"Error dialing from {device_id}: {e}")
                return False
    
    async def hangup_call(self, device_id: str) -> bool:
        """Hang up active call"""
        modem = self.modems.get(device_id)
        if not modem:
            return False
        
        async with self.command_lock:
            try:
                # Hang up call
                response = await self._send_at_command(modem, "ATH", timeout=10)
                success = response and "OK" in response
                
                if success:
                    modem.status = ModemStatus.IDLE
                
                logger.info(f"Hangup call on {device_id}: {'success' if success else 'failed'}")
                return success
                
            except Exception as e:
                logger.error(f"Error hanging up call on {device_id}: {e}")
                return False
    
    async def answer_call(self, device_id: str) -> bool:
        """Answer incoming call"""
        modem = self.modems.get(device_id)
        if not modem:
            return False
        
        async with self.command_lock:
            try:
                # Answer call
                response = await self._send_at_command(modem, "ATA", timeout=10)
                success = response and "OK" in response
                
                if success:
                    modem.status = ModemStatus.BUSY
                
                logger.info(f"Answer call on {device_id}: {'success' if success else 'failed'}")
                return success
                
            except Exception as e:
                logger.error(f"Error answering call on {device_id}: {e}")
                return False
    
    def get_available_modems(self) -> List[str]:
        """Get list of available (idle) modems"""
        return [
            device_id for device_id, modem in self.modems.items()
            if modem.status == ModemStatus.IDLE and modem.network_registered
        ]
    
    def get_modem_by_number(self, phone_number: str) -> Optional[str]:
        """Get modem device ID by phone number"""
        for device_id, modem in self.modems.items():
            if modem.phone_number == phone_number:
                return device_id
        return None
    
    async def cleanup(self):
        """Cleanup modem controller"""
        logger.info("🧹 Cleaning up modem controller...")
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        for modem in self.modems.values():
            if modem.serial_connection and modem.serial_connection.is_open:
                try:
                    modem.serial_connection.close()
                except:
                    pass
        
        self.modems.clear()
        logger.info("🧹 Modem controller cleanup complete")