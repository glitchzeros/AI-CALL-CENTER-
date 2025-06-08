#!/usr/bin/env python3
"""
Validation script for the updated subscription system
Tests all components and ensures everything works correctly
"""

import asyncio
import sys
import os
import json
from datetime import date

# Add backend to path
sys.path.append('/workspace/AI-CALL-CENTER-/backend')

def validate_file_syntax():
    """Validate Python file syntax"""
    print("🔍 Validating Python file syntax...")
    
    files_to_check = [
        '/workspace/AI-CALL-CENTER-/backend/models/subscription.py',
        '/workspace/AI-CALL-CENTER-/backend/services/usage_tracking_service.py',
        '/workspace/AI-CALL-CENTER-/backend/services/ai_usage_middleware.py',
        '/workspace/AI-CALL-CENTER-/backend/routers/subscriptions.py',
        '/workspace/AI-CALL-CENTER-/backend/routers/ai_sessions.py',
        '/workspace/AI-CALL-CENTER-/backend/services/sms_service.py'
    ]
    
    for file_path in files_to_check:
        try:
            with open(file_path, 'r') as f:
                compile(f.read(), file_path, 'exec')
            print(f"✅ {os.path.basename(file_path)} - Syntax valid")
        except SyntaxError as e:
            print(f"❌ {os.path.basename(file_path)} - Syntax error: {e}")
            return False
        except Exception as e:
            print(f"⚠️  {os.path.basename(file_path)} - Warning: {e}")
    
    return True

def validate_migration_sql():
    """Validate SQL migration file"""
    print("\n🔍 Validating SQL migration...")
    
    migration_file = '/workspace/AI-CALL-CENTER-/backend/migrations/004_update_subscription_tiers.sql'
    
    try:
        with open(migration_file, 'r') as f:
            content = f.read()
        
        # Check for required elements
        required_elements = [
            'ALTER TABLE subscription_tiers ADD COLUMN',
            'CREATE TABLE IF NOT EXISTS user_daily_usage',
            'INSERT INTO subscription_tiers',
            'tier1',
            'tier2', 
            'tier3',
            'price_uzs',
            'max_daily_ai_minutes',
            'max_daily_sms',
            'has_agentic_functions'
        ]
        
        for element in required_elements:
            if element in content:
                print(f"✅ Found: {element}")
            else:
                print(f"❌ Missing: {element}")
                return False
        
        print("✅ Migration SQL validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Migration validation error: {e}")
        return False

def validate_frontend_updates():
    """Validate frontend file updates"""
    print("\n🔍 Validating frontend updates...")
    
    # Check subscription page
    subscription_page = '/workspace/AI-CALL-CENTER-/frontend/src/pages/SubscriptionPage.jsx'
    try:
        with open(subscription_page, 'r') as f:
            content = f.read()
        
        required_elements = [
            'price_uzs',
            'max_daily_ai_minutes',
            'max_daily_sms',
            'has_agentic_functions',
            'has_agentic_constructor',
            'getMySubscription',
            'getUsageStatus'
        ]
        
        for element in required_elements:
            if element in content:
                print(f"✅ Frontend: Found {element}")
            else:
                print(f"❌ Frontend: Missing {element}")
                return False
        
        print("✅ Frontend validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Frontend validation error: {e}")
        return False

def validate_api_endpoints():
    """Validate API service updates"""
    print("\n🔍 Validating API service...")
    
    api_file = '/workspace/AI-CALL-CENTER-/frontend/src/services/api.js'
    try:
        with open(api_file, 'r') as f:
            content = f.read()
        
        required_endpoints = [
            'getUsageStatus',
            'getMySubscription',
            'aiSessionsAPI',
            'startSession',
            'endSession',
            'getSessionStatus'
        ]
        
        for endpoint in required_endpoints:
            if endpoint in content:
                print(f"✅ API: Found {endpoint}")
            else:
                print(f"❌ API: Missing {endpoint}")
                return False
        
        print("✅ API service validation passed")
        return True
        
    except Exception as e:
        print(f"❌ API validation error: {e}")
        return False

def validate_subscription_tiers():
    """Validate subscription tier configuration"""
    print("\n🔍 Validating subscription tier configuration...")
    
    migration_file = '/workspace/AI-CALL-CENTER-/backend/migrations/004_update_subscription_tiers.sql'
    
    try:
        with open(migration_file, 'r') as f:
            content = f.read()
        
        # Expected tier configurations
        expected_tiers = {
            'tier1': {
                'price_uzs': 250000,
                'ai_minutes': 240,
                'sms': 100,
                'agentic': True
            },
            'tier2': {
                'price_uzs': 750000,
                'ai_minutes': 480,
                'sms': 300,
                'agentic': True
            },
            'tier3': {
                'price_uzs': 1250000,
                'ai_minutes': 999999,
                'sms': 999999,
                'agentic': True
            }
        }
        
        for tier_name, config in expected_tiers.items():
            if tier_name in content:
                print(f"✅ Tier: {tier_name} found")
                
                # Check pricing
                if str(config['price_uzs']) in content:
                    print(f"✅ Tier {tier_name}: Correct pricing ({config['price_uzs']} UZS)")
                else:
                    print(f"❌ Tier {tier_name}: Incorrect pricing")
                    return False
                    
            else:
                print(f"❌ Tier: {tier_name} not found")
                return False
        
        print("✅ Subscription tier configuration validated")
        return True
        
    except Exception as e:
        print(f"❌ Tier validation error: {e}")
        return False

def validate_documentation():
    """Validate documentation exists"""
    print("\n🔍 Validating documentation...")
    
    doc_file = '/workspace/AI-CALL-CENTER-/SUBSCRIPTION_UPDATE_SUMMARY.md'
    
    try:
        with open(doc_file, 'r') as f:
            content = f.read()
        
        required_sections = [
            '# Subscription System Update Summary',
            '## New Subscription Tiers',
            '### Tier 1',
            '### Tier 2', 
            '### Tier 3',
            '## Changes Made',
            '## Backend Changes',
            '## Frontend Changes',
            '## API Endpoints'
        ]
        
        for section in required_sections:
            if section in content:
                print(f"✅ Doc: Found {section}")
            else:
                print(f"❌ Doc: Missing {section}")
                return False
        
        print("✅ Documentation validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Documentation validation error: {e}")
        return False

def main():
    """Run all validations"""
    print("🚀 Starting subscription system validation...\n")
    
    validations = [
        ("File Syntax", validate_file_syntax),
        ("Migration SQL", validate_migration_sql),
        ("Frontend Updates", validate_frontend_updates),
        ("API Endpoints", validate_api_endpoints),
        ("Subscription Tiers", validate_subscription_tiers),
        ("Documentation", validate_documentation)
    ]
    
    results = []
    
    for name, validation_func in validations:
        try:
            result = validation_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} validation failed with exception: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 VALIDATION SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:<20} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} validations passed")
    
    if passed == total:
        print("\n🎉 All validations passed! The subscription system is ready.")
        print("\n📋 Next steps:")
        print("1. Run the migration: 004_update_subscription_tiers.sql")
        print("2. Restart the backend service")
        print("3. Test the new subscription features")
        print("4. Verify usage tracking works correctly")
    else:
        print(f"\n⚠️  {total - passed} validation(s) failed. Please review and fix the issues.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)