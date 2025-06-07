"""
Admin Management Models
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class KeyType(str, Enum):
    COMPANY = "company"
    CLIENT = "client"


class KeyStatus(str, Enum):
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    EXPIRED = "expired"
    DISABLED = "disabled"


class ModemStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class ModemRole(str, Enum):
    COMPANY_NUMBER = "company_number"
    CLIENT_NUMBER = "client_number"
    UNASSIGNED = "unassigned"


class AdminLevel(str, Enum):
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    MODERATOR = "moderator"


# Gemini API Key Models
class GeminiApiKeyBase(BaseModel):
    api_key: str = Field(..., min_length=20, max_length=255)
    key_type: KeyType
    daily_limit: int = Field(default=1000, ge=100, le=10000)
    monthly_limit: int = Field(default=30000, ge=1000, le=1000000)
    notes: Optional[str] = None


class GeminiApiKeyCreate(GeminiApiKeyBase):
    pass


class GeminiApiKeyUpdate(BaseModel):
    status: Optional[KeyStatus] = None
    daily_limit: Optional[int] = Field(None, ge=100, le=10000)
    monthly_limit: Optional[int] = Field(None, ge=1000, le=1000000)
    notes: Optional[str] = None


class GeminiApiKey(GeminiApiKeyBase):
    id: str
    status: KeyStatus
    assigned_to: Optional[str] = None
    assigned_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    usage_count: int = 0
    last_used_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# GSM Modem Models
class GSMModemBase(BaseModel):
    device_path: str = Field(..., pattern=r'^/dev/(tty|cu)[A-Za-z0-9]+$')
    device_name: Optional[str] = None
    usb_port: Optional[str] = None
    phone_number: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    imei: Optional[str] = Field(None, pattern=r'^\d{15}$')
    sim_card_id: Optional[str] = None
    carrier: Optional[str] = None
    role_type: ModemRole = ModemRole.UNASSIGNED
    assigned_to_company: Optional[str] = None
    audio_device: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = {}


class GSMModemCreate(GSMModemBase):
    pass


class GSMModemUpdate(BaseModel):
    device_name: Optional[str] = None
    usb_port: Optional[str] = None
    phone_number: Optional[str] = Field(None, pattern=r'^\+?[1-9]\d{1,14}$')
    role_type: Optional[ModemRole] = None
    assigned_to_company: Optional[str] = None
    audio_device: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None
    status: Optional[ModemStatus] = None


class GSMModem(GSMModemBase):
    id: str
    signal_strength: Optional[int] = None
    status: ModemStatus
    last_seen_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Company Number Configuration Models
class CompanyNumberConfigBase(BaseModel):
    company_number: str = Field(..., min_length=3, max_length=50)
    system_prompt: str = Field(..., min_length=10, max_length=5000)
    ai_personality: str = Field(default="professional", pattern=r'^[a-z_]+$')
    voice_settings: Optional[Dict[str, Any]] = {}
    is_active: bool = True


class CompanyNumberConfigCreate(CompanyNumberConfigBase):
    gemini_api_key_id: Optional[str] = None
    modem_assignment_id: Optional[str] = None


class CompanyNumberConfigUpdate(BaseModel):
    system_prompt: Optional[str] = Field(None, min_length=10, max_length=5000)
    ai_personality: Optional[str] = Field(None, pattern=r'^[a-z_]+$')
    voice_settings: Optional[Dict[str, Any]] = None
    gemini_api_key_id: Optional[str] = None
    modem_assignment_id: Optional[str] = None
    is_active: Optional[bool] = None


class CompanyNumberConfig(CompanyNumberConfigBase):
    id: str
    gemini_api_key_id: Optional[str] = None
    modem_assignment_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Client API Assignment Models
class ClientApiAssignmentBase(BaseModel):
    user_id: str
    subscription_start: datetime
    subscription_end: datetime
    auto_renew: bool = False


class ClientApiAssignmentCreate(ClientApiAssignmentBase):
    pass


class ClientApiAssignmentUpdate(BaseModel):
    subscription_end: Optional[datetime] = None
    auto_renew: Optional[bool] = None


class ClientApiAssignment(ClientApiAssignmentBase):
    id: str
    gemini_api_key_id: Optional[str] = None
    usage_stats: Optional[Dict[str, Any]] = {}
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Admin Dashboard Models
class AdminDashboardStats(BaseModel):
    available_client_keys: int
    assigned_client_keys: int
    company_keys: int
    online_modems: int
    unassigned_modems: int
    active_subscribers: int
    active_api_assignments: int


class ModemAssignmentView(BaseModel):
    id: str
    device_path: str
    device_name: Optional[str]
    usb_port: Optional[str]
    phone_number: Optional[str]
    status: ModemStatus
    role_type: ModemRole
    assigned_to_company: Optional[str]
    system_prompt: Optional[str]
    assigned_api_key: Optional[str]
    signal_strength: Optional[int]
    last_seen_at: Optional[datetime]


class ApiKeyAssignmentView(BaseModel):
    id: str
    email: str
    company_number: Optional[str]
    api_key: str
    key_status: KeyStatus
    subscription_start: datetime
    subscription_end: datetime
    auto_renew: bool
    usage_count: int
    daily_limit: int
    monthly_limit: int
    subscription_status: str


# Bulk Operations
class BulkApiKeyCreate(BaseModel):
    api_keys: List[str] = Field(..., min_items=1, max_items=50)
    key_type: KeyType
    daily_limit: int = Field(default=1000, ge=100, le=10000)
    monthly_limit: int = Field(default=30000, ge=1000, le=1000000)


class BulkModemUpdate(BaseModel):
    modem_ids: List[str] = Field(..., min_items=1, max_items=20)
    role_type: Optional[ModemRole] = None
    status: Optional[ModemStatus] = None


# API Key Assignment Request
class AssignApiKeyRequest(BaseModel):
    user_id: str
    subscription_months: int = Field(..., ge=1, le=12)
    auto_renew: bool = False


class UnassignApiKeyRequest(BaseModel):
    user_id: str
    return_to_pool: bool = True


# Modem Assignment Request
class AssignModemRequest(BaseModel):
    modem_id: str
    company_number: str
    role_type: ModemRole
    gemini_api_key_id: Optional[str] = None


# System Prompt Templates
class SystemPromptTemplate(BaseModel):
    name: str
    description: str
    template: str
    variables: List[str] = []
    category: str = "general"


# Usage Statistics
class ApiKeyUsageStats(BaseModel):
    api_key_id: str
    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    tokens_used_today: int
    tokens_used_month: int
    last_24h_usage: List[Dict[str, Any]]


class ModemUsageStats(BaseModel):
    modem_id: str
    total_calls: int
    successful_calls: int
    failed_calls: int
    average_call_duration: float
    uptime_percentage: float
    last_24h_activity: List[Dict[str, Any]]


# Validation helpers
def validate_api_key_format(api_key: str) -> bool:
    """Validate Gemini API key format"""
    return api_key.startswith('AIzaSy') and len(api_key) >= 39


def validate_device_path(device_path: str) -> bool:
    """Validate device path format"""
    import re
    return bool(re.match(r'^/dev/(tty|cu)[A-Za-z0-9]+$', device_path))


# Custom validators
@validator('api_key')
def validate_gemini_api_key(cls, v):
    if not validate_api_key_format(v):
        raise ValueError('Invalid Gemini API key format')
    return v