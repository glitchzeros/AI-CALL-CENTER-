"""
Admin Service for managing API keys, modems, and configurations
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_, func, text
from sqlalchemy.orm import selectinload

from models.admin import *
from database.connection import get_database
from services.gemini_client import GeminiClient
from utils.exceptions import ValidationError, NotFoundError, ConflictError

logger = logging.getLogger("aetherium.admin")


class AdminService:
    """Service for admin operations"""
    
    def __init__(self):
        self.gemini_client = GeminiClient()
    
    # ==================== API Key Management ====================
    
    async def create_api_key(self, db: AsyncSession, api_key_data: GeminiApiKeyCreate) -> GeminiApiKey:
        """Create a new Gemini API key"""
        try:
            # Validate API key format
            if not self._validate_api_key_format(api_key_data.api_key):
                raise ValidationError("Invalid Gemini API key format")
            
            # Check if API key already exists
            existing = await self._get_api_key_by_key(db, api_key_data.api_key)
            if existing:
                raise ConflictError("API key already exists")
            
            # Test API key validity
            if not await self._test_api_key_validity(api_key_data.api_key):
                raise ValidationError("API key is not valid or has no quota")
            
            # Create new API key record
            query = text("""
                INSERT INTO gemini_api_keys (api_key, key_type, daily_limit, monthly_limit, notes)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
            """)
            
            result = await db.execute(query, (
                api_key_data.api_key,
                api_key_data.key_type.value,
                api_key_data.daily_limit,
                api_key_data.monthly_limit,
                api_key_data.notes
            ))
            
            api_key_record = result.fetchone()
            await db.commit()
            
            logger.info(f"Created new {api_key_data.key_type} API key: {api_key_data.api_key[:20]}...")
            return GeminiApiKey(**dict(api_key_record))
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create API key: {e}")
            raise
    
    async def bulk_create_api_keys(self, db: AsyncSession, bulk_data: BulkApiKeyCreate) -> List[GeminiApiKey]:
        """Create multiple API keys at once"""
        created_keys = []
        failed_keys = []
        
        for api_key in bulk_data.api_keys:
            try:
                key_data = GeminiApiKeyCreate(
                    api_key=api_key,
                    key_type=bulk_data.key_type,
                    daily_limit=bulk_data.daily_limit,
                    monthly_limit=bulk_data.monthly_limit
                )
                created_key = await self.create_api_key(db, key_data)
                created_keys.append(created_key)
            except Exception as e:
                failed_keys.append({"api_key": api_key, "error": str(e)})
                logger.warning(f"Failed to create API key {api_key[:20]}...: {e}")
        
        if failed_keys:
            logger.warning(f"Failed to create {len(failed_keys)} out of {len(bulk_data.api_keys)} API keys")
        
        return created_keys
    
    async def get_available_client_api_key(self, db: AsyncSession) -> Optional[GeminiApiKey]:
        """Get an available client API key from the pool"""
        query = text("""
            SELECT * FROM gemini_api_keys 
            WHERE key_type = 'client' AND status = 'available'
            ORDER BY created_at ASC
            LIMIT 1
        """)
        
        result = await db.execute(query)
        api_key_record = result.fetchone()
        
        if api_key_record:
            return GeminiApiKey(**dict(api_key_record))
        return None
    
    async def assign_api_key_to_user(self, db: AsyncSession, request: AssignApiKeyRequest) -> ClientApiAssignment:
        """Assign an API key to a user with subscription"""
        try:
            # Check if user already has an active assignment
            existing_assignment = await self._get_active_user_assignment(db, request.user_id)
            if existing_assignment:
                raise ConflictError("User already has an active API key assignment")
            
            # Get available API key
            api_key = await self.get_available_client_api_key(db)
            if not api_key:
                raise NotFoundError("No available API keys in the pool")
            
            # Calculate subscription dates
            start_date = datetime.utcnow()
            end_date = start_date + timedelta(days=30 * request.subscription_months)
            
            # Mark API key as assigned
            await db.execute(
                text("UPDATE gemini_api_keys SET status = 'assigned', assigned_to = $1, assigned_at = $2 WHERE id = $3"),
                (request.user_id, start_date, api_key.id)
            )
            
            # Create assignment record
            assignment_query = text("""
                INSERT INTO client_api_assignments (user_id, gemini_api_key_id, subscription_start, subscription_end, auto_renew)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING *
            """)
            
            result = await db.execute(assignment_query, (
                request.user_id,
                api_key.id,
                start_date,
                end_date,
                request.auto_renew
            ))
            
            assignment_record = result.fetchone()
            await db.commit()
            
            logger.info(f"Assigned API key to user {request.user_id} until {end_date}")
            return ClientApiAssignment(**dict(assignment_record))
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to assign API key to user {request.user_id}: {e}")
            raise
    
    async def unassign_api_key_from_user(self, db: AsyncSession, request: UnassignApiKeyRequest) -> bool:
        """Unassign API key from user and return to pool"""
        try:
            # Get user's current assignment
            assignment = await self._get_active_user_assignment(db, request.user_id)
            if not assignment:
                raise NotFoundError("User has no active API key assignment")
            
            # Update assignment end date
            await db.execute(
                text("UPDATE client_api_assignments SET subscription_end = $1 WHERE user_id = $2 AND subscription_end > $1"),
                (datetime.utcnow(), request.user_id)
            )
            
            if request.return_to_pool:
                # Return API key to available pool
                await db.execute(
                    text("UPDATE gemini_api_keys SET status = 'available', assigned_to = NULL WHERE id = $1"),
                    (assignment.gemini_api_key_id,)
                )
                logger.info(f"Returned API key to pool from user {request.user_id}")
            else:
                # Mark as expired
                await db.execute(
                    text("UPDATE gemini_api_keys SET status = 'expired' WHERE id = $1"),
                    (assignment.gemini_api_key_id,)
                )
                logger.info(f"Marked API key as expired for user {request.user_id}")
            
            await db.commit()
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to unassign API key from user {request.user_id}: {e}")
            raise
    
    # ==================== Modem Management ====================
    
    async def detect_connected_modems(self, db: AsyncSession) -> List[GSMModem]:
        """Detect and register connected GSM modems"""
        import serial.tools.list_ports
        import serial
        
        detected_modems = []
        
        # Scan for USB/Serial devices
        ports = serial.tools.list_ports.comports()
        
        for port in ports:
            try:
                # Try to connect to the device
                ser = serial.Serial(port.device, 115200, timeout=1)
                
                # Send AT command to check if it's a modem
                ser.write(b'AT\r\n')
                response = ser.read(100).decode('utf-8', errors='ignore')
                
                if 'OK' in response:
                    # It's a modem, get more info
                    modem_info = await self._get_modem_info(ser)
                    
                    # Check if already in database
                    existing = await self._get_modem_by_device_path(db, port.device)
                    
                    if existing:
                        # Update existing modem
                        await self._update_modem_status(db, existing.id, ModemStatus.ONLINE, modem_info)
                        detected_modems.append(existing)
                    else:
                        # Create new modem record
                        modem_data = GSMModemCreate(
                            device_path=port.device,
                            device_name=port.description or f"Modem on {port.device}",
                            usb_port=getattr(port, 'location', None),
                            phone_number=modem_info.get('phone_number'),
                            imei=modem_info.get('imei'),
                            carrier=modem_info.get('carrier')
                        )
                        
                        new_modem = await self.create_modem(db, modem_data)
                        detected_modems.append(new_modem)
                
                ser.close()
                
            except Exception as e:
                logger.debug(f"Device {port.device} is not a modem: {e}")
                continue
        
        logger.info(f"Detected {len(detected_modems)} GSM modems")
        return detected_modems
    
    async def create_modem(self, db: AsyncSession, modem_data: GSMModemCreate) -> GSMModem:
        """Create a new GSM modem record"""
        try:
            query = text("""
                INSERT INTO gsm_modems (device_path, device_name, usb_port, phone_number, imei, sim_card_id, 
                                      carrier, role_type, assigned_to_company, audio_device, configuration, status)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, 'offline')
                RETURNING *
            """)
            
            result = await db.execute(query, (
                modem_data.device_path,
                modem_data.device_name,
                modem_data.usb_port,
                modem_data.phone_number,
                modem_data.imei,
                modem_data.sim_card_id,
                modem_data.carrier,
                modem_data.role_type.value,
                modem_data.assigned_to_company,
                modem_data.audio_device,
                modem_data.configuration
            ))
            
            modem_record = result.fetchone()
            await db.commit()
            
            logger.info(f"Created new modem: {modem_data.device_path}")
            return GSMModem(**dict(modem_record))
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to create modem: {e}")
            raise
    
    async def assign_modem_to_company(self, db: AsyncSession, request: AssignModemRequest) -> bool:
        """Assign a modem to a company number"""
        try:
            # Verify modem exists and is available
            modem = await self._get_modem_by_id(db, request.modem_id)
            if not modem:
                raise NotFoundError("Modem not found")
            
            if modem.role_type != ModemRole.UNASSIGNED:
                raise ConflictError("Modem is already assigned")
            
            # Update modem assignment
            await db.execute(
                text("UPDATE gsm_modems SET role_type = $1, assigned_to_company = $2 WHERE id = $3"),
                (request.role_type.value, request.company_number, request.modem_id)
            )
            
            # Update or create company number configuration
            if request.gemini_api_key_id:
                await db.execute(
                    text("""
                    INSERT INTO company_number_configs (company_number, modem_assignment_id, gemini_api_key_id, system_prompt)
                    VALUES ($1, $2, $3, 'Default system prompt for company number ' || $1)
                    ON CONFLICT (company_number) DO UPDATE SET
                        modem_assignment_id = EXCLUDED.modem_assignment_id,
                        gemini_api_key_id = EXCLUDED.gemini_api_key_id
                    """),
                    (request.company_number, request.modem_id, request.gemini_api_key_id)
                )
            
            await db.commit()
            logger.info(f"Assigned modem {request.modem_id} to company {request.company_number}")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to assign modem: {e}")
            raise
    
    # ==================== Company Number Configuration ====================
    
    async def update_company_config(self, db: AsyncSession, company_number: str, config_data: CompanyNumberConfigUpdate) -> CompanyNumberConfig:
        """Update company number configuration"""
        try:
            # Check if configuration exists
            existing = await self._get_company_config(db, company_number)
            
            if existing:
                # Update existing configuration
                update_fields = []
                values = []
                param_count = 1
                
                for field, value in config_data.dict(exclude_unset=True).items():
                    if value is not None:
                        update_fields.append(f"{field} = ${param_count}")
                        values.append(value)
                        param_count += 1
                
                if update_fields:
                    values.append(company_number)
                    query = f"""
                        UPDATE company_number_configs 
                        SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                        WHERE company_number = ${param_count}
                        RETURNING *
                    """
                    
                    result = await db.execute(query, values)
                    config_record = result.fetchone()
            else:
                # Create new configuration
                query = text("""
                    INSERT INTO company_number_configs (company_number, system_prompt, ai_personality, voice_settings, 
                                                      gemini_api_key_id, modem_assignment_id, is_active)
                    VALUES ($1, $2, $3, $4, $5, $6, $7)
                    RETURNING *
                """)
                
                result = await db.execute(query, (
                    company_number,
                    config_data.system_prompt or f"Default system prompt for {company_number}",
                    config_data.ai_personality or "professional",
                    config_data.voice_settings or {},
                    config_data.gemini_api_key_id,
                    config_data.modem_assignment_id,
                    config_data.is_active if config_data.is_active is not None else True
                ))
                
                config_record = result.fetchone()
            
            await db.commit()
            logger.info(f"Updated configuration for company number {company_number}")
            return CompanyNumberConfig(**dict(config_record))
            
        except Exception as e:
            await db.rollback()
            logger.error(f"Failed to update company config: {e}")
            raise
    
    # ==================== Dashboard and Statistics ====================
    
    async def get_dashboard_stats(self, db: AsyncSession) -> AdminDashboardStats:
        """Get admin dashboard statistics"""
        query = text("SELECT * FROM admin_dashboard_stats")
        result = await db.execute(query)
        stats_record = result.fetchone()
        
        if stats_record:
            return AdminDashboardStats(**dict(stats_record))
        
        # Fallback if view doesn't work
        return AdminDashboardStats(
            available_client_keys=0,
            assigned_client_keys=0,
            company_keys=0,
            online_modems=0,
            unassigned_modems=0,
            active_subscribers=0,
            active_api_assignments=0
        )
    
    async def get_modem_assignments(self, db: AsyncSession) -> List[ModemAssignmentView]:
        """Get all modem assignments with details"""
        query = text("SELECT * FROM modem_assignments_view ORDER BY device_path")
        result = await db.execute(query)
        
        assignments = []
        for record in result.fetchall():
            assignments.append(ModemAssignmentView(**dict(record)))
        
        return assignments
    
    async def get_api_key_assignments(self, db: AsyncSession) -> List[ApiKeyAssignmentView]:
        """Get all API key assignments with details"""
        query = "SELECT * FROM api_key_assignments_view ORDER BY subscription_end DESC"
        result = await db.execute(query)
        
        assignments = []
        for record in result.fetchall():
            assignments.append(ApiKeyAssignmentView(**dict(record)))
        
        return assignments
    
    # ==================== Background Tasks ====================
    
    async def cleanup_expired_assignments(self, db: AsyncSession) -> int:
        """Clean up expired API key assignments and return keys to pool"""
        try:
            # Skip cleanup - API key tables don't exist yet
            # TODO: Implement when API key management is added
            logger.debug("🧹 Skipped expired assignments cleanup (tables not implemented)")
            return 0
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired assignments: {e}")
            await db.rollback()
            raise
    
    async def update_modem_status(self, db: AsyncSession) -> int:
        """Update status of all modems by checking connectivity"""
        updated_count = 0
        
        # Get all modems
        query = text("SELECT * FROM gsm_modems WHERE status != 'maintenance'")
        result = await db.execute(query)
        modems = result.fetchall()
        
        for modem in modems:
            try:
                # Try to connect to modem
                import serial
                ser = serial.Serial(modem.device_path, 115200, timeout=1)
                ser.write(b'AT\r\n')
                response = ser.read(100).decode('utf-8', errors='ignore')
                ser.close()
                
                if 'OK' in response:
                    # Modem is online
                    if modem.status != 'online':
                        await db.execute(
                            text("UPDATE gsm_modems SET status = 'online', last_seen_at = CURRENT_TIMESTAMP WHERE id = $1"),
                            (modem.id,)
                        )
                        updated_count += 1
                else:
                    # Modem is not responding
                    if modem.status != 'error':
                        await db.execute(
                            text("UPDATE gsm_modems SET status = 'error' WHERE id = $1"),
                            (modem.id,)
                        )
                        updated_count += 1
                        
            except Exception:
                # Modem is offline
                if modem.status != 'offline':
                    await db.execute(
                        text("UPDATE gsm_modems SET status = 'offline' WHERE id = $1"),
                        (modem.id,)
                    )
                    updated_count += 1
        
        await db.commit()
        
        if updated_count > 0:
            logger.info(f"Updated status for {updated_count} modems")
        
        return updated_count
    
    # ==================== Helper Methods ====================
    
    def _validate_api_key_format(self, api_key: str) -> bool:
        """Validate Gemini API key format"""
        return api_key.startswith('AIzaSy') and len(api_key) >= 39
    
    async def _test_api_key_validity(self, api_key: str) -> bool:
        """Test if API key is valid by making a test request"""
        try:
            test_client = GeminiClient(api_key=api_key)
            response = await test_client.generate_response("Test", max_tokens=1)
            return response is not None
        except Exception:
            return False
    
    async def _get_api_key_by_key(self, db: AsyncSession, api_key: str) -> Optional[GeminiApiKey]:
        """Get API key record by key value"""
        query = "SELECT * FROM gemini_api_keys WHERE api_key = $1"
        result = await db.execute(query, (api_key,))
        record = result.fetchone()
        
        if record:
            return GeminiApiKey(**dict(record))
        return None
    
    async def _get_active_user_assignment(self, db: AsyncSession, user_id: str) -> Optional[ClientApiAssignment]:
        """Get active API key assignment for user"""
        query = text("""
            SELECT * FROM client_api_assignments 
            WHERE user_id = $1 AND subscription_end > CURRENT_TIMESTAMP
            ORDER BY subscription_end DESC
            LIMIT 1
        """)
        result = await db.execute(query, (user_id,))
        record = result.fetchone()
        
        if record:
            return ClientApiAssignment(**dict(record))
        return None
    
    async def _get_modem_by_device_path(self, db: AsyncSession, device_path: str) -> Optional[GSMModem]:
        """Get modem by device path"""
        query = text("SELECT * FROM gsm_modems WHERE device_path = $1")
        result = await db.execute(query, (device_path,))
        record = result.fetchone()
        
        if record:
            return GSMModem(**dict(record))
        return None
    
    async def _get_modem_by_id(self, db: AsyncSession, modem_id: str) -> Optional[GSMModem]:
        """Get modem by ID"""
        query = text("SELECT * FROM gsm_modems WHERE id = $1")
        result = await db.execute(query, (modem_id,))
        record = result.fetchone()
        
        if record:
            return GSMModem(**dict(record))
        return None
    
    async def _get_company_config(self, db: AsyncSession, company_number: str) -> Optional[CompanyNumberConfig]:
        """Get company number configuration"""
        query = text("SELECT * FROM company_number_configs WHERE company_number = $1")
        result = await db.execute(query, (company_number,))
        record = result.fetchone()
        
        if record:
            return CompanyNumberConfig(**dict(record))
        return None
    
    async def _get_modem_info(self, serial_connection) -> Dict[str, Any]:
        """Get detailed information from modem"""
        info = {}
        
        try:
            # Get phone number
            serial_connection.write(b'AT+CNUM\r\n')
            response = serial_connection.read(200).decode('utf-8', errors='ignore')
            if '+CNUM:' in response:
                import re
                match = re.search(r'\+CNUM: ".*","(\+?\d+)"', response)
                if match:
                    info['phone_number'] = match.group(1)
            
            # Get IMEI
            serial_connection.write(b'AT+CGSN\r\n')
            response = serial_connection.read(100).decode('utf-8', errors='ignore')
            lines = response.split('\n')
            for line in lines:
                if line.strip().isdigit() and len(line.strip()) == 15:
                    info['imei'] = line.strip()
                    break
            
            # Get carrier info
            serial_connection.write(b'AT+COPS?\r\n')
            response = serial_connection.read(100).decode('utf-8', errors='ignore')
            if '+COPS:' in response:
                import re
                match = re.search(r'\+COPS: \d+,\d+,"([^"]+)"', response)
                if match:
                    info['carrier'] = match.group(1)
                    
        except Exception as e:
            logger.debug(f"Failed to get modem info: {e}")
        
        return info
    
    async def _update_modem_status(self, db: AsyncSession, modem_id: str, status: ModemStatus, info: Dict[str, Any]):
        """Update modem status and information"""
        await db.execute(
            text("""
            UPDATE gsm_modems 
            SET status = $1, last_seen_at = CURRENT_TIMESTAMP,
                phone_number = COALESCE($2, phone_number),
                imei = COALESCE($3, imei),
                carrier = COALESCE($4, carrier)
            WHERE id = $5
            """),
            (status.value, info.get('phone_number'), info.get('imei'), info.get('carrier'), modem_id)
        )