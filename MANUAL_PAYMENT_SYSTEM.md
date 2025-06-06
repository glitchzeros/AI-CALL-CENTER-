# Manual Bank Transfer Payment System

## Overview

The Aetherium platform now uses a manual bank transfer payment system instead of Click API integration. This system provides a more direct payment flow where clients receive bank details after AI consultation and make transfers directly to the company's bank account.

## Payment Flow

### 1. Client Signup & Consultation
- Client registers and selects subscription tier
- AI consultation begins via phone call
- During consultation, payment ritual invocation is triggered

### 2. Payment Initiation
- System creates 30-minute payment session
- Generates unique reference code (format: AET + 10 digits)
- Converts USD pricing to UZS using current exchange rate
- Displays bank details to client with countdown timer

### 3. Bank Transfer
- Client transfers money to company bank account
- Must include reference code in transfer description
- Transfer amount must match exact UZS amount shown

### 4. SMS Confirmation
- Bank sends SMS notification to company phone number
- GSM module receives SMS and forwards to payment service
- AI analyzes SMS content to confirm payment
- System activates subscription if payment confirmed

## Technical Implementation

### Database Schema

```sql
-- Manual payment sessions table
CREATE TABLE manual_payment_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    tier_name VARCHAR(50) NOT NULL,
    tier_price_usd DECIMAL(10,2) NOT NULL,
    amount_uzs DECIMAL(15,2) NOT NULL,
    reference_code VARCHAR(20) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    company_number VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    confirmed_at TIMESTAMP,
    sms_content TEXT,
    INDEX idx_reference_code (reference_code),
    INDEX idx_status_expires (status, expires_at),
    INDEX idx_company_number (company_number)
);

-- Updated subscription tiers with UZS pricing
ALTER TABLE subscription_tiers ADD COLUMN price_uzs DECIMAL(15,2);
UPDATE subscription_tiers SET price_uzs = price_usd * 12300; -- Current exchange rate
```

### Environment Variables

```bash
# Company Bank Information
COMPANY_BANK_CARD=8600123456789012
COMPANY_BANK_NAME=Xalq Banki
COMPANY_CARDHOLDER_NAME=Aetherium LLC
COMPANY_BANK_PHONE=+998901234567
```

### API Endpoints

#### Initiate Payment
```
POST /api/payments/initiate-consultation
{
    "tier_name": "Apprentice",
    "tier_price_usd": 20.00
}

Response:
{
    "success": true,
    "payment_id": "manual_1749238914_1",
    "reference_code": "AET0000018914",
    "amount_uzs": 246000,
    "expires_at": "2025-06-06T20:11:54.404777",
    "payment_instructions": {...},
    "bank_details": {...}
}
```

#### Confirm SMS Payment
```
POST /api/payments/confirm-sms
{
    "sms_content": "Karta 8600****9012 ga 246,000 so'm o'tkazma qabul qilindi. AET0000018914",
    "sender_number": "+998901111111"
}

Response:
{
    "success": true,
    "confirmed": true,
    "user_id": 1,
    "tier_name": "Apprentice"
}
```

#### Check Payment Status
```
GET /api/payments/status/{payment_id}

Response:
{
    "success": true,
    "status": "pending",
    "remaining_minutes": 25.5,
    "amount_uzs": 246000,
    "reference_code": "AET0000018914"
}
```

#### Cancel Payment
```
POST /api/payments/cancel/{payment_id}

Response:
{
    "success": true,
    "message": "Payment session cancelled"
}
```

## Frontend Integration

### Payment Instructions Modal

The frontend displays a modal with:
- Company bank details
- Transfer amount in UZS
- Reference code (with copy button)
- 30-minute countdown timer
- Payment instructions in multiple languages

### Key Components

```jsx
// PaymentInstructionsModal.jsx
const PaymentInstructionsModal = ({ isOpen, onClose, paymentData }) => {
    const [timeLeft, setTimeLeft] = useState(30 * 60); // 30 minutes
    
    // Countdown timer logic
    useEffect(() => {
        const timer = setInterval(() => {
            setTimeLeft(prev => {
                if (prev <= 1) {
                    onClose();
                    return 0;
                }
                return prev - 1;
            });
        }, 1000);
        
        return () => clearInterval(timer);
    }, [onClose]);
    
    // Copy reference code functionality
    const copyReferenceCode = () => {
        navigator.clipboard.writeText(paymentData.reference_code);
    };
    
    // Display bank details and instructions
};
```

## SMS Processing

### AI Analysis

The system uses AI to analyze incoming SMS messages:

```python
async def analyze_sms_for_payment(self, sms_content: str, reference_code: str, amount_uzs: float) -> dict:
    """Analyze SMS content to determine if it confirms a payment"""
    
    prompt = f"""
    Analyze this SMS message to determine if it confirms a bank transfer payment:
    
    SMS Content: {sms_content}
    Expected Reference Code: {reference_code}
    Expected Amount: {amount_uzs:,.0f} UZS
    
    Look for:
    1. Transfer confirmation keywords (o'tkazma, перевод, transfer, qabul qilindi, получен, received)
    2. Amount matching {amount_uzs:,.0f} (allow ±1000 UZS tolerance)
    3. Reference code {reference_code} or similar pattern
    4. Card number ending in the company card digits
    
    Respond with JSON:
    {{
        "is_payment_confirmation": true/false,
        "confidence": 0.0-1.0,
        "reason": "explanation",
        "extracted_amount": amount_found,
        "extracted_reference": "reference_found"
    }}
    """
    
    # Send to Gemini for analysis
    response = await self.gemini_client.analyze_text(prompt)
    return json.loads(response)
```

### SMS Handler Integration

```python
# modem-manager/sms_handler.py
async def handle_incoming_sms(self, sender: str, content: str, modem_number: str):
    """Process incoming SMS and check for payment confirmations"""
    
    # Forward to manual payment service
    payment_result = await self.manual_payment_service.process_sms_confirmation(
        sms_content=content,
        sender_number=sender
    )
    
    if payment_result["success"] and payment_result["confirmed"]:
        logger.info(f"Payment confirmed via SMS for user {payment_result['user_id']}")
        # Activate subscription
        await self.activate_user_subscription(
            user_id=payment_result["user_id"],
            tier_name=payment_result["tier_name"]
        )
```

## Workflow Engine Integration

### Payment Ritual Invocation

```python
async def _execute_payment_ritual(self, context: ExecutionContext, config: Dict[str, Any]) -> InvocationResult:
    """Execute Payment Ritual invocation - Manual bank transfer payment"""
    
    # Get configuration
    tier_name = config.get("tier_name", "Apprentice")
    reassurance_script = config.get("reassurance_script", "")
    
    # Initiate payment session
    payment_result = await payment_service.initiate_consultation_payment(
        user_id=context.session.user_id,
        tier_name=tier_name,
        tier_price_usd=tier_price,
        company_number=context.session.company_number
    )
    
    if payment_result["success"]:
        # Generate multilingual payment instructions
        instruction_texts = {
            "uz": f"To'lov uchun {payment_result['amount_uzs']:,.0f} so'm miqdorini {bank_info['bank_card']} karta raqamiga o'tkazing. Reference kod: {payment_result['reference_code']}",
            "ru": f"Для оплаты переведите {payment_result['amount_uzs']:,.0f} сум на карту {bank_info['bank_card']}. Код ссылки: {payment_result['reference_code']}",
            "en": f"For payment, transfer {payment_result['amount_uzs']:,.0f} UZS to card {bank_info['bank_card']}. Reference code: {payment_result['reference_code']}"
        }
        
        # Select language and generate TTS
        detected_language = context.variables.get("detected_language", "uz")
        instruction_text = instruction_texts.get(detected_language, instruction_texts["uz"])
        
        audio_data = await self.edge_tts_client.synthesize_speech(
            text=instruction_text,
            language=detected_language,
            voice_settings={"pitch": "-5%", "rate": "-10%"}
        )
        
        # Set session state for payment confirmation
        context.variables["awaiting_payment"] = True
        context.variables["payment_id"] = payment_result["payment_id"]
        context.variables["reference_code"] = payment_result["reference_code"]
        
        return InvocationResult(success=True, requires_wait=True, wait_condition="payment_confirmation")
```

## Security Considerations

### Data Protection
- Bank card numbers are encrypted at rest
- Reference codes are unique and time-limited
- Payment sessions expire automatically after 30 minutes
- SMS content is logged for audit purposes only

### Fraud Prevention
- AI analysis prevents false positive confirmations
- Amount tolerance checking (±1000 UZS)
- Reference code validation
- Time-based session expiration

### Access Control
- Payment endpoints require authentication
- SMS processing is restricted to company numbers
- Admin-only access to payment logs

## Monitoring & Maintenance

### Background Tasks
- Automatic cleanup of expired payment sessions every 5 minutes
- Payment status monitoring
- SMS processing queue management

### Logging
- All payment initiations logged
- SMS confirmations tracked
- Failed payment attempts recorded
- System errors captured for debugging

### Metrics
- Payment success rate
- Average confirmation time
- SMS processing accuracy
- Session expiration rates

## Troubleshooting

### Common Issues

1. **SMS Not Received**
   - Check GSM module connectivity
   - Verify company phone number configuration
   - Check SMS handler service status

2. **Payment Not Confirmed**
   - Verify reference code in transfer description
   - Check amount matches exactly (±1000 UZS tolerance)
   - Ensure SMS contains confirmation keywords

3. **Session Expired**
   - Payment window is 30 minutes only
   - Client must initiate new payment session
   - Previous reference codes become invalid

### Debug Commands

```bash
# Check payment service logs
docker logs aetherium_backend | grep "manual_payment"

# Monitor SMS processing
docker logs aetherium_modem_manager | grep "sms_handler"

# Check database payment sessions
psql -d aetherium -c "SELECT * FROM manual_payment_sessions WHERE status = 'pending';"
```

## Migration Notes

### From Click API
- All Click API endpoints removed
- Environment variables updated
- Frontend payment flow completely redesigned
- Database schema extended for manual payments
- Workflow engine payment ritual updated

### Backward Compatibility
- Existing user accounts preserved
- Subscription tiers maintained with UZS pricing added
- Company numbers remain unchanged
- SMS infrastructure reused for confirmations