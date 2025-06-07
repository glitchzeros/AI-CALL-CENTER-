"""
Aetherium Environment Configuration System
Automatically switches between demo and real variables based on availability
"""

import os
from typing import Dict, Any, Optional
from pathlib import Path
import json

class EnvironmentConfig:
    """Smart environment configuration that falls back to demo values when real ones aren't available"""
    
    def __init__(self):
        self.config = {}
        self.demo_config = self._load_demo_config()
        self.real_config = self._load_real_config()
        self._merge_configs()
    
    def _load_demo_config(self) -> Dict[str, Any]:
        """Load demo configuration values"""
        return {
            # Database Configuration (Demo)
            "POSTGRES_DB": "aetherium_demo",
            "POSTGRES_USER": "demo_user",
            "POSTGRES_PASSWORD": "demo_password_123",
            "DATABASE_URL": "postgresql+asyncpg://demo_user:demo_password_123@database:5432/aetherium_demo",
            
            # JWT Configuration (Demo)
            "JWT_SECRET_KEY": "demo_jwt_secret_key_for_development_only_32_chars",
            "JWT_ALGORITHM": "HS256",
            "JWT_ACCESS_TOKEN_EXPIRE_MINUTES": "1440",
            
            # Encryption Key (Demo)
            "ENCRYPTION_KEY": "demo_encryption_key_32_characters",
            
            # API Keys (Demo)
            "GEMINI_API_KEY": "AIzaSyDemo_Key_Replace_With_Real_Gemini_API_Key",
            
            # Payment API (Demo)
            "CLICK_MERCHANT_ID": "demo_merchant_id",
            "CLICK_SERVICE_ID": "demo_service_id",
            "CLICK_SECRET_KEY": "demo_secret_key",
            "CLICK_API_URL": "https://api.click.uz/v2",
            
            # Telegram Bot (Demo)
            "TELEGRAM_BOT_TOKEN": "demo_bot_token_replace_with_real",
            
            # SMS Configuration (Demo)
            "SMS_API_KEY": "demo_sms_api_key",
            "SMS_API_URL": "https://api.sms.uz/v1",
            
            # Backend Configuration
            "BACKEND_API_URL": "http://backend-api:8000",
            "MODEM_MANAGER_URL": "http://modem-manager:8001",
            
            # CORS Configuration
            "CORS_ORIGINS": '["http://localhost:12000", "http://localhost:3000"]',
            
            # System Configuration
            "LOG_LEVEL": "INFO",
            "MAX_CONCURRENT_SESSIONS": "40",
            "MODEM_SCAN_INTERVAL": "30",
            "AUDIO_SAMPLE_RATE": "16000",
            "AUDIO_CHANNELS": "1",
            "AUDIO_CHUNK_SIZE": "1024",
            "WS_HEARTBEAT_INTERVAL": "30",
            
            # Demo Company Information
            "COMPANY_BANK_CARD": "8600 1234 5678 9012",
            "COMPANY_BANK_NAME": "Demo Bank",
            "COMPANY_CARDHOLDER_NAME": "Demo Company LLC",
            "COMPANY_BANK_PHONE": "+998901234567"
        }
    
    def _load_real_config(self) -> Dict[str, Any]:
        """Load real configuration from environment variables"""
        real_config = {}
        
        # Check for real environment variables
        env_vars = [
            "POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD", "DATABASE_URL",
            "JWT_SECRET_KEY", "JWT_ALGORITHM", "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
            "ENCRYPTION_KEY", "GEMINI_API_KEY", "CLICK_MERCHANT_ID", "CLICK_SERVICE_ID",
            "CLICK_SECRET_KEY", "CLICK_API_URL", "TELEGRAM_BOT_TOKEN", "SMS_API_KEY",
            "SMS_API_URL", "BACKEND_API_URL", "MODEM_MANAGER_URL", "CORS_ORIGINS",
            "LOG_LEVEL", "MAX_CONCURRENT_SESSIONS", "MODEM_SCAN_INTERVAL",
            "AUDIO_SAMPLE_RATE", "AUDIO_CHANNELS", "AUDIO_CHUNK_SIZE",
            "WS_HEARTBEAT_INTERVAL", "COMPANY_BANK_CARD", "COMPANY_BANK_NAME",
            "COMPANY_CARDHOLDER_NAME", "COMPANY_BANK_PHONE"
        ]
        
        for var in env_vars:
            value = os.getenv(var)
            if value and value.strip() and not self._is_placeholder(value):
                real_config[var] = value
        
        return real_config
    
    def _is_placeholder(self, value: str) -> bool:
        """Check if a value is a placeholder that should be replaced"""
        placeholders = [
            "your_", "demo_", "replace_with", "change_in_production",
            "here", "placeholder", "example"
        ]
        value_lower = value.lower()
        return any(placeholder in value_lower for placeholder in placeholders)
    
    def _merge_configs(self):
        """Merge demo and real configs, preferring real values when available"""
        self.config = self.demo_config.copy()
        self.config.update(self.real_config)
        
        # Log which values are using demo vs real
        self._log_config_status()
    
    def _log_config_status(self):
        """Log which configuration values are demo vs real"""
        demo_count = 0
        real_count = 0
        
        for key in self.demo_config.keys():
            if key in self.real_config:
                real_count += 1
            else:
                demo_count += 1
        
        print(f"🔧 Configuration Status:")
        print(f"   ✅ Real values: {real_count}")
        print(f"   🎭 Demo values: {demo_count}")
        print(f"   📊 Total: {real_count + demo_count}")
        
        if demo_count > 0:
            print(f"   ⚠️  Using demo values for: {', '.join([k for k in self.demo_config.keys() if k not in self.real_config])}")
    
    def get(self, key: str, default: Optional[str] = None) -> str:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return self.config.copy()
    
    def is_demo_mode(self) -> bool:
        """Check if running in demo mode (any demo values present)"""
        return len(self.real_config) < len(self.demo_config)
    
    def get_demo_keys(self) -> list:
        """Get list of keys using demo values"""
        return [k for k in self.demo_config.keys() if k not in self.real_config]
    
    def get_real_keys(self) -> list:
        """Get list of keys using real values"""
        return list(self.real_config.keys())
    
    def export_env_file(self, filepath: str = ".env.generated"):
        """Export current configuration to .env file"""
        env_path = Path(filepath)
        
        with open(env_path, 'w') as f:
            f.write("# Aetherium Environment Configuration\n")
            f.write("# Auto-generated configuration file\n")
            f.write(f"# Generated on: {os.popen('date').read().strip()}\n\n")
            
            # Group configurations
            groups = {
                "Database Configuration": ["POSTGRES_DB", "POSTGRES_USER", "POSTGRES_PASSWORD", "DATABASE_URL"],
                "JWT Configuration": ["JWT_SECRET_KEY", "JWT_ALGORITHM", "JWT_ACCESS_TOKEN_EXPIRE_MINUTES"],
                "Encryption": ["ENCRYPTION_KEY"],
                "API Keys": ["GEMINI_API_KEY"],
                "Payment Configuration": ["CLICK_MERCHANT_ID", "CLICK_SERVICE_ID", "CLICK_SECRET_KEY", "CLICK_API_URL"],
                "Telegram Bot": ["TELEGRAM_BOT_TOKEN"],
                "SMS Configuration": ["SMS_API_KEY", "SMS_API_URL"],
                "Backend Configuration": ["BACKEND_API_URL", "MODEM_MANAGER_URL"],
                "CORS Configuration": ["CORS_ORIGINS"],
                "System Configuration": ["LOG_LEVEL", "MAX_CONCURRENT_SESSIONS", "MODEM_SCAN_INTERVAL"],
                "Audio Configuration": ["AUDIO_SAMPLE_RATE", "AUDIO_CHANNELS", "AUDIO_CHUNK_SIZE"],
                "WebSocket Configuration": ["WS_HEARTBEAT_INTERVAL"],
                "Company Information": ["COMPANY_BANK_CARD", "COMPANY_BANK_NAME", "COMPANY_CARDHOLDER_NAME", "COMPANY_BANK_PHONE"]
            }
            
            for group_name, keys in groups.items():
                f.write(f"# {group_name}\n")
                for key in keys:
                    if key in self.config:
                        value = self.config[key]
                        status = "REAL" if key in self.real_config else "DEMO"
                        f.write(f"{key}={value}  # {status}\n")
                f.write("\n")
        
        print(f"📄 Configuration exported to: {env_path}")
        return env_path

# Global configuration instance
config = EnvironmentConfig()

def get_config() -> EnvironmentConfig:
    """Get the global configuration instance"""
    return config

def setup_environment():
    """Setup environment variables from configuration"""
    for key, value in config.get_all().items():
        os.environ[key] = str(value)
    
    # Export to .env file for Docker
    config.export_env_file(".env.generated")
    
    return config

if __name__ == "__main__":
    # Test the configuration system
    config = setup_environment()
    print("\n🚀 Aetherium Configuration System")
    print(f"Demo mode: {'Yes' if config.is_demo_mode() else 'No'}")
    print(f"Database URL: {config.get('DATABASE_URL')}")
    print(f"Gemini API Key: {config.get('GEMINI_API_KEY')[:20]}...")