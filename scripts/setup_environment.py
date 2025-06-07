#!/usr/bin/env python3
"""
Aetherium Environment Setup Script
Automatically configures the environment for demo or production use
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.environment import setup_environment, get_config

def main():
    """Main setup function"""
    print("🏛️ Aetherium Environment Setup")
    print("=" * 50)
    
    # Setup environment
    config = setup_environment()
    
    # Display configuration status
    print(f"\n📊 Configuration Summary:")
    print(f"   Mode: {'Demo' if config.is_demo_mode() else 'Production'}")
    print(f"   Real values: {len(config.get_real_keys())}")
    print(f"   Demo values: {len(config.get_demo_keys())}")
    
    # Show important configurations
    print(f"\n🔑 Key Configurations:")
    print(f"   Database: {config.get('DATABASE_URL')}")
    print(f"   JWT Secret: {'Set' if config.get('JWT_SECRET_KEY') else 'Not set'}")
    print(f"   Gemini API: {'Real' if 'GEMINI_API_KEY' in config.get_real_keys() else 'Demo'}")
    print(f"   Telegram Bot: {'Real' if 'TELEGRAM_BOT_TOKEN' in config.get_real_keys() else 'Demo'}")
    
    # Export environment file
    env_file = config.export_env_file()
    print(f"\n✅ Environment configured successfully!")
    print(f"   Configuration file: {env_file}")
    
    if config.is_demo_mode():
        print(f"\n⚠️  Running in DEMO mode")
        print(f"   To use real values, set environment variables:")
        for key in config.get_demo_keys()[:5]:  # Show first 5
            print(f"   export {key}=your_real_value")
        if len(config.get_demo_keys()) > 5:
            print(f"   ... and {len(config.get_demo_keys()) - 5} more")
    
    return config

if __name__ == "__main__":
    main()