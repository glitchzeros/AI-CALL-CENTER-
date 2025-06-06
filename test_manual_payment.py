#!/usr/bin/env python3
"""
Test script for manual payment system
"""

import asyncio
import os
import sys
sys.path.append('backend')

from services.manual_payment_service import ManualPaymentService

async def test_manual_payment():
    """Test the manual payment service"""
    
    # Set environment variables for testing
    os.environ['COMPANY_BANK_CARD'] = '8600123456789012'
    os.environ['COMPANY_BANK_NAME'] = 'Xalq Banki'
    os.environ['COMPANY_CARDHOLDER_NAME'] = 'Aetherium LLC'
    os.environ['COMPANY_BANK_PHONE'] = '+998901234567'
    
    payment_service = ManualPaymentService()
    
    print("=== Testing Manual Payment Service ===")
    
    # Test 1: Initiate payment
    print("\n1. Testing payment initiation...")
    result = await payment_service.initiate_consultation_payment(
        user_id=1,
        tier_name="Apprentice",
        tier_price_usd=20.00,
        company_number="+998901234567"
    )
    
    if result["success"]:
        print("✅ Payment initiation successful")
        print(f"   Payment ID: {result['payment_id']}")
        print(f"   Reference Code: {result['reference_code']}")
        print(f"   Amount UZS: {result['amount_uzs']:,.0f}")
        print(f"   Expires: {result['expires_at']}")
        
        payment_id = result["payment_id"]
        reference_code = result["reference_code"]
        
        # Test 2: Check payment status
        print("\n2. Testing payment status check...")
        status_result = await payment_service.check_payment_status(payment_id)
        
        if status_result["success"]:
            print("✅ Payment status check successful")
            print(f"   Status: {status_result['status']}")
            print(f"   Remaining minutes: {status_result['remaining_minutes']:.1f}")
        else:
            print("❌ Payment status check failed")
            print(f"   Error: {status_result['error']}")
        
        # Test 3: SMS analysis
        print("\n3. Testing SMS payment confirmation...")
        
        # Test SMS samples
        test_sms_samples = [
            f"Karta 8600****9012 ga {result['amount_uzs']:,.0f} so'm o'tkazma qabul qilindi. {reference_code}",
            f"Перевод {result['amount_uzs']:,.0f} сум получен на карту 8600****9012. Код: {reference_code}",
            f"Transfer of {result['amount_uzs']:,.0f} UZS received to card 8600****9012. Reference: {reference_code}",
            "Bu oddiy SMS, to'lov bilan bog'liq emas",
            f"Karta 8600****9012 ga 50000 so'm o'tkazma. Boshqa reference kod: ABC123"
        ]
        
        for i, sms_content in enumerate(test_sms_samples, 1):
            print(f"\n   Testing SMS {i}: {sms_content[:50]}...")
            
            sms_result = await payment_service.process_sms_confirmation(
                sms_content=sms_content,
                sender_number="+998901111111"
            )
            
            if sms_result["success"]:
                if sms_result["confirmed"]:
                    print(f"   ✅ SMS {i}: Payment CONFIRMED")
                    print(f"      User ID: {sms_result.get('user_id')}")
                    print(f"      Tier: {sms_result.get('tier_name')}")
                    break  # Stop after first confirmation
                else:
                    print(f"   ℹ️  SMS {i}: Not a payment confirmation")
                    print(f"      Reason: {sms_result.get('reason')}")
            else:
                print(f"   ❌ SMS {i}: Processing failed")
                print(f"      Error: {sms_result.get('error')}")
        
        # Test 4: Cleanup
        print("\n4. Testing cleanup...")
        await payment_service.cleanup_expired_sessions()
        print("✅ Cleanup completed")
        
    else:
        print("❌ Payment initiation failed")
        print(f"   Error: {result['error']}")
    
    # Test 5: Bank info
    print("\n5. Testing bank info retrieval...")
    bank_info = payment_service.get_company_bank_info()
    print("✅ Bank info retrieved")
    print(f"   Card: {bank_info['bank_card']}")
    print(f"   Bank: {bank_info['bank_name']}")
    print(f"   Cardholder: {bank_info['cardholder_name']}")
    
    print("\n=== Manual Payment Service Test Complete ===")

if __name__ == "__main__":
    asyncio.run(test_manual_payment())