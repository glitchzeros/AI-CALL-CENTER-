"""
GSM Module Management Router
The Scribe's Communication Hardware Management
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from pydantic import BaseModel
from typing import Optional, List
import logging
import secrets
from datetime import datetime

from database.connection import get_database
from models.gsm_module import GSMModule, PaymentSession
from routers.auth import get_current_user
from models.user import User
from services.gsm_service import GSMService

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic models
class GSMModuleCreate(BaseModel):
    phone_number: str
    bank_card_number: str
    bank_name: str
    card_holder_name: str
    device_id: Optional[str] = None
    description: Optional[str] = None
    priority: int = 1

class GSMModuleUpdate(BaseModel):
    phone_number: Optional[str] = None
    bank_card_number: Optional[str] = None
    bank_name: Optional[str] = None
    card_holder_name: Optional[str] = None
    device_id: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    is_active: Optional[bool] = None
    is_available: Optional[bool] = None

class GSMModuleResponse(BaseModel):
    id: int
    phone_number: str
    bank_card_number: str
    bank_name: str
    card_holder_name: str
    device_id: Optional[str]
    is_active: bool
    is_available: bool
    description: Optional[str]
    priority: int
    status: str
    last_used_at: Optional[str]
    created_at: str
    updated_at: str

class PaymentSessionResponse(BaseModel):
    id: int
    user_id: int
    subscription_tier: str
    amount_uzs: int
    amount_usd: int
    bank_card_number: str
    bank_name: str
    card_holder_name: str
    status: str
    created_at: str
    expires_at: str
    confirmed_at: Optional[str]

@router.get("/", response_model=List[GSMModuleResponse])
async def get_gsm_modules(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Get all GSM modules
    Admin only endpoint
    """
    try:
        gsm_service = GSMService()
        modules = await gsm_service.get_gsm_modules(db)
        
        return [
            GSMModuleResponse(
                id=module.id,
                phone_number=module.phone_number,
                bank_card_number=module.bank_card_number,
                bank_name=module.bank_name,
                card_holder_name=module.card_holder_name,
                device_id=module.device_id,
                is_active=module.is_active,
                is_available=module.is_available,
                description=module.description,
                priority=module.priority,
                status=module.status,
                last_used_at=module.last_used_at.isoformat() if module.last_used_at else None,
                created_at=module.created_at.isoformat(),
                updated_at=module.updated_at.isoformat()
            )
            for module in modules
        ]
        
    except Exception as e:
        logger.error(f"Error getting GSM modules: {e}")
        raise HTTPException(status_code=500, detail="Failed to get GSM modules")

@router.post("/", response_model=GSMModuleResponse)
async def create_gsm_module(
    module_data: GSMModuleCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_database)
):
    """
    Create new GSM module
    Admin only endpoint
    """
    try:
        gsm_service = GSMService()
        module = await gsm_service.create_gsm_module(
            db=db,
            phone_number=module_data.phone_number,
            bank_card_number=module_data.bank_card_number,
            bank_name=module_data.bank_name,
            card_holder_name=module_data.card_holder_name,
            device_id=module_data.device_id,
            description=module_data.description,
            priority=module_data.priority
        )
        
        return GSMModuleResponse(
            id=module.id,
            phone_number=module.phone_number,
            bank_card_number=module.bank_card_number,
            bank_name=module.bank_name,
            card_holder_name=module.card_holder_name,
            device_id=module.device_id,
            is_active=module.is_active,
            is_available=module.is_available,
            description=module.description,
            priority=module.priority,
            status=module.status,
            last_used_at=module.last_used_at.isoformat() if module.last_used_at else None,
            created_at=module.created_at.isoformat(),
            updated_at=module.updated_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Error creating GSM module: {e}")
        raise HTTPException(status_code=500, detail="Failed to create GSM module")

@router.put("/{module_id}", response_model=GSMModuleResponse)
async def update_gsm_module(
    module_id: int,
    module_data: GSMModuleUpdate,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """
    Update a GSM module
    The Scribe's Hardware Modification
    """
    try:
        # Find the module
        result = await db.execute(select(GSMModem).where(GSMModem.id == module_id))
        module = result.scalar_one_or_none()
        
        if not module:
            raise HTTPException(status_code=404, detail="GSM module not found")
        
        # Update fields
        update_data = {}
        if module_data.device_id is not None:
            update_data["device_id"] = module_data.device_id
        if module_data.phone_number is not None:
            update_data["phone_number"] = module_data.phone_number
        if module_data.control_port is not None:
            update_data["control_port"] = module_data.control_port
        if module_data.audio_port is not None:
            update_data["audio_port"] = module_data.audio_port
        if module_data.bank_card_number is not None:
            update_data["bank_card_number"] = module_data.bank_card_number
        if module_data.bank_card_holder_name is not None:
            update_data["bank_card_holder_name"] = module_data.bank_card_holder_name
        if module_data.status is not None:
            update_data["status"] = module_data.status
        if module_data.is_demo_mode is not None:
            update_data["is_demo_mode"] = module_data.is_demo_mode
            # Generate new demo code if switching to demo mode
            if module_data.is_demo_mode and not module.is_demo_mode:
                update_data["demo_sms_code"] = f"{secrets.randbelow(900000) + 100000:06d}"
            elif not module_data.is_demo_mode:
                update_data["demo_sms_code"] = None
        
        if update_data:
            await db.execute(
                update(GSMModem).where(GSMModem.id == module_id).values(**update_data)
            )
            await db.commit()
            
            # Log the action
            management_log = GSMModuleManagement(
                modem_id=module_id,
                action_type="update",
                performed_by=current_user.id,
                action_data=f"Updated GSM module {module.device_id}: {list(update_data.keys())}"
            )
            db.add(management_log)
            await db.commit()
        
        # Fetch updated module
        result = await db.execute(select(GSMModem).where(GSMModem.id == module_id))
        updated_module = result.scalar_one()
        
        logger.info(f"GSM module updated: {updated_module.device_id} by user {current_user.email}")
        
        return GSMModuleResponse(
            id=updated_module.id,
            device_id=updated_module.device_id,
            phone_number=updated_module.phone_number,
            control_port=updated_module.control_port,
            audio_port=updated_module.audio_port,
            status=updated_module.status,
            signal_strength=updated_module.signal_strength,
            bank_card_number=updated_module.bank_card_number,
            bank_card_holder_name=updated_module.bank_card_holder_name,
            is_demo_mode=updated_module.is_demo_mode,
            demo_sms_code=updated_module.demo_sms_code if updated_module.is_demo_mode else None,
            assigned_user_id=updated_module.assigned_user_id,
            created_at=updated_module.created_at
        )
        
    except Exception as e:
        logger.error(f"Error updating GSM module: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update GSM module")

@router.delete("/{module_id}")
async def delete_gsm_module(
    module_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """
    Delete a GSM module
    The Scribe's Hardware Removal
    """
    try:
        # Find the module
        result = await db.execute(select(GSMModem).where(GSMModem.id == module_id))
        module = result.scalar_one_or_none()
        
        if not module:
            raise HTTPException(status_code=404, detail="GSM module not found")
        
        # Log the action before deletion
        management_log = GSMModuleManagement(
            modem_id=module_id,
            action_type="delete",
            performed_by=current_user.id,
            action_data=f"Deleted GSM module {module.device_id}"
        )
        db.add(management_log)
        
        # Delete the module
        await db.execute(delete(GSMModem).where(GSMModem.id == module_id))
        await db.commit()
        
        logger.info(f"GSM module deleted: {module.device_id} by user {current_user.email}")
        
        return {"message": "GSM module deleted successfully"}
        
    except Exception as e:
        logger.error(f"Error deleting GSM module: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete GSM module")

@router.get("/demo-codes")
async def get_demo_codes(
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """
    Get demo SMS codes for all demo modules
    The Scribe's Demo Code Registry
    """
    try:
        result = await db.execute(
            select(GSMModem).where(GSMModem.is_demo_mode == True)
        )
        demo_modules = result.scalars().all()
        
        demo_codes = []
        for module in demo_modules:
            if module.demo_sms_code:
                demo_codes.append({
                    "phone_number": module.phone_number,
                    "demo_code": module.demo_sms_code,
                    "bank_card_number": module.bank_card_number,
                    "bank_card_holder_name": module.bank_card_holder_name
                })
        
        return {"demo_codes": demo_codes}
        
    except Exception as e:
        logger.error(f"Error fetching demo codes: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch demo codes")

@router.post("/{module_id}/regenerate-demo-code")
async def regenerate_demo_code(
    module_id: int,
    db: AsyncSession = Depends(get_database),
    current_user: User = Depends(get_current_user)
):
    """
    Regenerate demo SMS code for a module
    The Scribe's Demo Code Renewal
    """
    try:
        # Find the module
        result = await db.execute(select(GSMModem).where(GSMModem.id == module_id))
        module = result.scalar_one_or_none()
        
        if not module:
            raise HTTPException(status_code=404, detail="GSM module not found")
        
        if not module.is_demo_mode:
            raise HTTPException(status_code=400, detail="Module is not in demo mode")
        
        # Generate new demo code
        new_demo_code = f"{secrets.randbelow(900000) + 100000:06d}"
        
        await db.execute(
            update(GSMModem)
            .where(GSMModem.id == module_id)
            .values(demo_sms_code=new_demo_code)
        )
        await db.commit()
        
        # Log the action
        management_log = GSMModuleManagement(
            modem_id=module_id,
            action_type="regenerate_demo_code",
            performed_by=current_user.id,
            action_data=f"Regenerated demo code for {module.device_id}"
        )
        db.add(management_log)
        await db.commit()
        
        logger.info(f"Demo code regenerated for module {module.device_id} by user {current_user.email}")
        
        return {
            "message": "Demo code regenerated successfully",
            "new_demo_code": new_demo_code
        }
        
    except Exception as e:
        logger.error(f"Error regenerating demo code: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Failed to regenerate demo code")