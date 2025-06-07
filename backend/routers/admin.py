"""
Admin API Routes
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import logging

from database.connection import get_database
from models.admin import *
from services.admin_service import AdminService
from utils.auth import get_current_admin_user
from utils.exceptions import ValidationError, NotFoundError, ConflictError

router = APIRouter(prefix="/api/admin", tags=["admin"])
security = HTTPBearer()
logger = logging.getLogger("aetherium.admin.api")

admin_service = AdminService()


# ==================== Authentication Dependency ====================

async def get_admin_user(token: str = Depends(security), db: AsyncSession = Depends(get_database)):
    """Verify admin user authentication"""
    try:
        admin_user = await get_current_admin_user(token.credentials, db)
        return admin_user
    except Exception as e:
        raise HTTPException(status_code=401, detail="Admin authentication required")


# ==================== Dashboard ====================

@router.get("/dashboard", response_model=AdminDashboardStats)
async def get_dashboard_stats(
    admin_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_database)
):
    """Get admin dashboard statistics"""
    try:
        stats = await admin_service.get_dashboard_stats(db)
        return stats
    except Exception as e:
        logger.error(f"Failed to get dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve dashboard statistics")


# ==================== API Key Management ====================

@router.post("/api-keys", response_model=GeminiApiKey)
async def create_api_key(
    api_key_data: GeminiApiKeyCreate,
    admin_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_database)
):
    """Create a new Gemini API key"""
    try:
        api_key = await admin_service.create_api_key(db, api_key_data)
        logger.info(f"Admin {admin_user.email} created new API key")
        return api_key
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to create API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to create API key")


@router.post("/api-keys/bulk", response_model=List[GeminiApiKey])
async def bulk_create_api_keys(
    bulk_data: BulkApiKeyCreate,
    admin_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_database)
):
    """Create multiple API keys at once"""
    try:
        api_keys = await admin_service.bulk_create_api_keys(db, bulk_data)
        logger.info(f"Admin {admin_user.email} bulk created {len(api_keys)} API keys")
        return api_keys
    except Exception as e:
        logger.error(f"Failed to bulk create API keys: {e}")
        raise HTTPException(status_code=500, detail="Failed to create API keys")


@router.get("/api-keys", response_model=List[GeminiApiKey])
async def get_api_keys(
    key_type: Optional[KeyType] = None,
    status: Optional[KeyStatus] = None,
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    admin_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_database)
):
    """Get list of API keys with filtering"""
    try:
        query = "SELECT * FROM gemini_api_keys WHERE 1=1"
        params = []
        param_count = 1
        
        if key_type:
            query += f" AND key_type = ${param_count}"
            params.append(key_type.value)
            param_count += 1
        
        if status:
            query += f" AND status = ${param_count}"
            params.append(status.value)
            param_count += 1
        
        query += f" ORDER BY created_at DESC LIMIT ${param_count} OFFSET ${param_count + 1}"
        params.extend([limit, offset])
        
        result = await db.execute(query, params)
        api_keys = []
        
        for record in result.fetchall():
            api_keys.append(GeminiApiKey(**dict(record)))
        
        return api_keys
    except Exception as e:
        logger.error(f"Failed to get API keys: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve API keys")


@router.put("/api-keys/{api_key_id}", response_model=GeminiApiKey)
async def update_api_key(
    api_key_id: str,
    update_data: GeminiApiKeyUpdate,
    admin_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_database)
):
    """Update an API key"""
    try:
        # Build update query
        update_fields = []
        values = []
        param_count = 1
        
        for field, value in update_data.dict(exclude_unset=True).items():
            if value is not None:
                update_fields.append(f"{field} = ${param_count}")
                values.append(value.value if hasattr(value, 'value') else value)
                param_count += 1
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        values.append(api_key_id)
        query = f"""
            UPDATE gemini_api_keys 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ${param_count}
            RETURNING *
        """
        
        result = await db.execute(query, values)
        api_key_record = result.fetchone()
        
        if not api_key_record:
            raise HTTPException(status_code=404, detail="API key not found")
        
        await db.commit()
        logger.info(f"Admin {admin_user.email} updated API key {api_key_id}")
        return GeminiApiKey(**dict(api_key_record))
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to update API key")


@router.delete("/api-keys/{api_key_id}")
async def delete_api_key(
    api_key_id: str,
    admin_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_database)
):
    """Delete an API key"""
    try:
        # Check if API key is assigned
        check_query = "SELECT assigned_to FROM gemini_api_keys WHERE id = $1"
        result = await db.execute(check_query, (api_key_id,))
        api_key_record = result.fetchone()
        
        if not api_key_record:
            raise HTTPException(status_code=404, detail="API key not found")
        
        if api_key_record.assigned_to:
            raise HTTPException(status_code=400, detail="Cannot delete assigned API key")
        
        # Delete the API key
        await db.execute("DELETE FROM gemini_api_keys WHERE id = $1", (api_key_id,))
        await db.commit()
        
        logger.info(f"Admin {admin_user.email} deleted API key {api_key_id}")
        return {"success": True, "message": "API key deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete API key: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete API key")


# ==================== User API Key Assignment ====================

@router.post("/users/{user_id}/assign-api-key", response_model=ClientApiAssignment)
async def assign_api_key_to_user(
    user_id: str,
    request: AssignApiKeyRequest,
    admin_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_database)
):
    """Assign an API key to a user"""
    try:
        request.user_id = user_id  # Ensure user_id matches URL parameter
        assignment = await admin_service.assign_api_key_to_user(db, request)
        logger.info(f"Admin {admin_user.email} assigned API key to user {user_id}")
        return assignment
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to assign API key to user: {e}")
        raise HTTPException(status_code=500, detail="Failed to assign API key")


@router.post("/users/{user_id}/unassign-api-key")
async def unassign_api_key_from_user(
    user_id: str,
    request: UnassignApiKeyRequest,
    admin_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_database)
):
    """Unassign API key from a user"""
    try:
        request.user_id = user_id
        success = await admin_service.unassign_api_key_from_user(db, request)
        logger.info(f"Admin {admin_user.email} unassigned API key from user {user_id}")
        return {"success": success, "message": "API key unassigned successfully"}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to unassign API key from user: {e}")
        raise HTTPException(status_code=500, detail="Failed to unassign API key")


@router.get("/api-key-assignments", response_model=List[ApiKeyAssignmentView])
async def get_api_key_assignments(
    admin_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_database)
):
    """Get all API key assignments"""
    try:
        assignments = await admin_service.get_api_key_assignments(db)
        return assignments
    except Exception as e:
        logger.error(f"Failed to get API key assignments: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve assignments")


# ==================== Modem Management ====================

@router.post("/modems/detect", response_model=List[GSMModem])
async def detect_modems(
    background_tasks: BackgroundTasks,
    admin_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_database)
):
    """Detect connected GSM modems"""
    try:
        modems = await admin_service.detect_connected_modems(db)
        logger.info(f"Admin {admin_user.email} detected {len(modems)} modems")
        return modems
    except Exception as e:
        logger.error(f"Failed to detect modems: {e}")
        raise HTTPException(status_code=500, detail="Failed to detect modems")


@router.post("/modems", response_model=GSMModem)
async def create_modem(
    modem_data: GSMModemCreate,
    admin_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_database)
):
    """Manually create a modem record"""
    try:
        modem = await admin_service.create_modem(db, modem_data)
        logger.info(f"Admin {admin_user.email} created modem {modem.device_path}")
        return modem
    except Exception as e:
        logger.error(f"Failed to create modem: {e}")
        raise HTTPException(status_code=500, detail="Failed to create modem")


@router.get("/modems", response_model=List[GSMModem])
async def get_modems(
    status: Optional[ModemStatus] = None,
    role_type: Optional[ModemRole] = None,
    admin_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_database)
):
    """Get list of modems with filtering"""
    try:
        query = "SELECT * FROM gsm_modems WHERE 1=1"
        params = []
        param_count = 1
        
        if status:
            query += f" AND status = ${param_count}"
            params.append(status.value)
            param_count += 1
        
        if role_type:
            query += f" AND role_type = ${param_count}"
            params.append(role_type.value)
            param_count += 1
        
        query += " ORDER BY device_path"
        
        result = await db.execute(query, params)
        modems = []
        
        for record in result.fetchall():
            modems.append(GSMModem(**dict(record)))
        
        return modems
    except Exception as e:
        logger.error(f"Failed to get modems: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve modems")


@router.put("/modems/{modem_id}", response_model=GSMModem)
async def update_modem(
    modem_id: str,
    update_data: GSMModemUpdate,
    admin_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_database)
):
    """Update a modem"""
    try:
        # Build update query
        update_fields = []
        values = []
        param_count = 1
        
        for field, value in update_data.dict(exclude_unset=True).items():
            if value is not None:
                update_fields.append(f"{field} = ${param_count}")
                values.append(value.value if hasattr(value, 'value') else value)
                param_count += 1
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        values.append(modem_id)
        query = f"""
            UPDATE gsm_modems 
            SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ${param_count}
            RETURNING *
        """
        
        result = await db.execute(query, values)
        modem_record = result.fetchone()
        
        if not modem_record:
            raise HTTPException(status_code=404, detail="Modem not found")
        
        await db.commit()
        logger.info(f"Admin {admin_user.email} updated modem {modem_id}")
        return GSMModem(**dict(modem_record))
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update modem: {e}")
        raise HTTPException(status_code=500, detail="Failed to update modem")


@router.post("/modems/{modem_id}/assign", response_model=dict)
async def assign_modem_to_company(
    modem_id: str,
    request: AssignModemRequest,
    admin_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_database)
):
    """Assign a modem to a company number"""
    try:
        request.modem_id = modem_id
        success = await admin_service.assign_modem_to_company(db, request)
        logger.info(f"Admin {admin_user.email} assigned modem {modem_id} to company {request.company_number}")
        return {"success": success, "message": "Modem assigned successfully"}
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to assign modem: {e}")
        raise HTTPException(status_code=500, detail="Failed to assign modem")


@router.get("/modem-assignments", response_model=List[ModemAssignmentView])
async def get_modem_assignments(
    admin_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_database)
):
    """Get all modem assignments with details"""
    try:
        assignments = await admin_service.get_modem_assignments(db)
        return assignments
    except Exception as e:
        logger.error(f"Failed to get modem assignments: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve modem assignments")


# ==================== Company Number Configuration ====================

@router.get("/company-configs", response_model=List[CompanyNumberConfig])
async def get_company_configs(
    admin_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_database)
):
    """Get all company number configurations"""
    try:
        query = "SELECT * FROM company_number_configs ORDER BY company_number"
        result = await db.execute(query)
        
        configs = []
        for record in result.fetchall():
            configs.append(CompanyNumberConfig(**dict(record)))
        
        return configs
    except Exception as e:
        logger.error(f"Failed to get company configs: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve company configurations")


@router.put("/company-configs/{company_number}", response_model=CompanyNumberConfig)
async def update_company_config(
    company_number: str,
    config_data: CompanyNumberConfigUpdate,
    admin_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_database)
):
    """Update company number configuration"""
    try:
        config = await admin_service.update_company_config(db, company_number, config_data)
        logger.info(f"Admin {admin_user.email} updated config for company {company_number}")
        return config
    except Exception as e:
        logger.error(f"Failed to update company config: {e}")
        raise HTTPException(status_code=500, detail="Failed to update company configuration")


@router.post("/company-configs", response_model=CompanyNumberConfig)
async def create_company_config(
    config_data: CompanyNumberConfigCreate,
    admin_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_database)
):
    """Create a new company number configuration"""
    try:
        query = """
            INSERT INTO company_number_configs (company_number, system_prompt, ai_personality, voice_settings, 
                                              gemini_api_key_id, modem_assignment_id, is_active)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
        """
        
        result = await db.execute(query, (
            config_data.company_number,
            config_data.system_prompt,
            config_data.ai_personality,
            config_data.voice_settings,
            config_data.gemini_api_key_id,
            config_data.modem_assignment_id,
            config_data.is_active
        ))
        
        config_record = result.fetchone()
        await db.commit()
        
        logger.info(f"Admin {admin_user.email} created config for company {config_data.company_number}")
        return CompanyNumberConfig(**dict(config_record))
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create company config: {e}")
        raise HTTPException(status_code=500, detail="Failed to create company configuration")


# ==================== Background Tasks ====================

@router.post("/tasks/cleanup-expired")
async def cleanup_expired_assignments(
    background_tasks: BackgroundTasks,
    admin_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_database)
):
    """Manually trigger cleanup of expired API key assignments"""
    try:
        cleaned_count = await admin_service.cleanup_expired_assignments(db)
        logger.info(f"Admin {admin_user.email} triggered cleanup, cleaned {cleaned_count} assignments")
        return {"success": True, "cleaned_count": cleaned_count}
    except Exception as e:
        logger.error(f"Failed to cleanup expired assignments: {e}")
        raise HTTPException(status_code=500, detail="Failed to cleanup expired assignments")


@router.post("/tasks/update-modem-status")
async def update_modem_status(
    background_tasks: BackgroundTasks,
    admin_user = Depends(get_admin_user),
    db: AsyncSession = Depends(get_database)
):
    """Manually trigger modem status update"""
    try:
        updated_count = await admin_service.update_modem_status(db)
        logger.info(f"Admin {admin_user.email} triggered modem status update, updated {updated_count} modems")
        return {"success": True, "updated_count": updated_count}
    except Exception as e:
        logger.error(f"Failed to update modem status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update modem status")


# ==================== System Prompt Templates ====================

@router.get("/prompt-templates", response_model=List[SystemPromptTemplate])
async def get_prompt_templates(
    admin_user = Depends(get_admin_user)
):
    """Get predefined system prompt templates"""
    templates = [
        SystemPromptTemplate(
            name="Professional Customer Service",
            description="Professional and helpful customer service assistant",
            template="You are a professional customer service AI assistant for {company_name}. Be helpful, polite, and efficient in your responses. Always maintain a professional tone and focus on solving customer problems.",
            variables=["company_name"],
            category="customer_service"
        ),
        SystemPromptTemplate(
            name="Technical Support",
            description="Technical support specialist for troubleshooting",
            template="You are a technical support AI specialist for {company_name}. Help users with technical issues, provide clear step-by-step solutions, and ask relevant questions to diagnose problems. Be patient and thorough in your explanations.",
            variables=["company_name"],
            category="technical"
        ),
        SystemPromptTemplate(
            name="Sales Assistant",
            description="Enthusiastic sales assistant for product promotion",
            template="You are a sales AI assistant for {company_name}. Be enthusiastic and help customers find the right products or services. Highlight benefits, answer questions about features, and guide customers through the purchasing process.",
            variables=["company_name"],
            category="sales"
        ),
        SystemPromptTemplate(
            name="Appointment Scheduler",
            description="Assistant for scheduling appointments and bookings",
            template="You are an appointment scheduling AI for {company_name}. Help customers book appointments, check availability, reschedule existing appointments, and provide information about services. Be clear about scheduling policies and requirements.",
            variables=["company_name"],
            category="scheduling"
        ),
        SystemPromptTemplate(
            name="Order Support",
            description="Assistant for order tracking and support",
            template="You are an order support AI for {company_name}. Help customers track orders, process returns, handle complaints, and provide information about shipping and delivery. Be empathetic and solution-focused.",
            variables=["company_name"],
            category="orders"
        )
    ]
    
    return templates