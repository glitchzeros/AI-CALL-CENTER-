# Subscription System Update Summary

## Overview
Updated the subscription system to implement the new pricing structure with UZS pricing and daily usage limits as requested.

## New Subscription Tiers

### Tier 1 (First Tier)
- **Price**: 250,000 UZS per month
- **Daily AI Call Processing**: 240 minutes (4 hours)
- **Daily SMS**: 100 SMS (incoming + outgoing)
- **Features**: 
  - Agentic functions access
  - Agentic functions constructor tab
  - Access until subscription expires

### Tier 2 (Second Tier)
- **Price**: 750,000 UZS per month
- **Daily AI Call Processing**: 480 minutes (8 hours)
- **Daily SMS**: 300 SMS (incoming + outgoing)
- **Features**: 
  - All features from Tier 1
  - Enhanced limits

### Tier 3 (Third Tier)
- **Price**: 1,250,000 UZS per month
- **Daily AI Call Processing**: Unlimited minutes
- **Daily SMS**: Unlimited SMS
- **Features**: 
  - All features from Tier 1
  - Unlimited usage
  - Priority support

## Changes Made

### Backend Changes

#### 1. Updated Subscription Model (`/backend/models/subscription.py`)
- Added `price_uzs` field for UZS pricing
- Added `max_daily_ai_minutes` for daily AI call processing limits
- Added `max_daily_sms` for daily SMS limits
- Added `has_agentic_functions` for agentic functions access
- Added `has_agentic_constructor` for agentic constructor access
- Maintained backward compatibility with existing fields

#### 2. Created Migration (`/backend/migrations/004_update_subscription_tiers.sql`)
- Added new columns to subscription_tiers table
- Updated subscription tiers with new pricing and limits
- Created `user_daily_usage` table for tracking daily usage
- Added appropriate indexes for performance

#### 3. Updated Subscription Router (`/backend/routers/subscriptions.py`)
- Updated `SubscriptionTierResponse` model to include new fields
- Modified tier listing to return new fields
- Updated payment calculation to use UZS pricing directly
- Added new endpoints:
  - `/usage-status` - Get current user's daily usage
  - `/my-subscription` - Get user's subscription details with usage

#### 4. Created Usage Tracking Service (`/backend/services/usage_tracking_service.py`)
- `UsageTrackingService` class for managing daily usage limits
- Methods to track AI minutes and SMS usage
- Methods to check usage limits before allowing operations
- Support for unlimited tiers (999999 = unlimited)

### Frontend Changes

#### 1. Updated Subscription Page (`/frontend/src/pages/SubscriptionPage.jsx`)
- Updated pricing display to use `price_uzs` field
- Added display for daily AI minutes and SMS limits
- Added display for agentic functions access
- Updated tier icons and colors for new tier names
- Maintained backward compatibility with old tier names

#### 2. Updated API Service (`/frontend/src/services/api.js`)
- Added new API endpoints:
  - `getUsageStatus()` - Get usage status
  - `getMySubscription()` - Get subscription details

## Key Features

### 1. Daily Usage Tracking
- Tracks AI call processing minutes per day
- Tracks SMS usage (incoming + outgoing) per day
- Resets daily at midnight
- Enforces limits based on subscription tier

### 2. Agentic Functions Access
- Controlled access to agentic functions based on subscription
- Constructor tab access for building custom functions
- Access maintained until subscription expires

### 3. UZS Pricing
- Direct UZS pricing without USD conversion
- Maintains USD pricing for compatibility
- Clear pricing display in frontend

### 4. Unlimited Tiers
- Tier 3 offers unlimited AI minutes and SMS
- Handled by setting limits to 999999 (treated as unlimited)

## Database Schema Changes

### New Columns in `subscription_tiers`
```sql
price_uzs INTEGER DEFAULT 0
max_daily_ai_minutes INTEGER DEFAULT 240
max_daily_sms INTEGER DEFAULT 100
has_agentic_functions BOOLEAN DEFAULT FALSE
has_agentic_constructor BOOLEAN DEFAULT FALSE
```

### New Table `user_daily_usage`
```sql
CREATE TABLE user_daily_usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    usage_date DATE NOT NULL,
    ai_minutes_used INTEGER DEFAULT 0,
    sms_count_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, usage_date)
);
```

## API Endpoints

### New Endpoints
- `GET /api/subscriptions/usage-status` - Get daily usage status
- `GET /api/subscriptions/my-subscription` - Get subscription details

### Updated Endpoints
- `GET /api/subscriptions/tiers` - Now returns new fields
- `POST /api/subscriptions/start-payment-monitoring` - Uses UZS pricing

## Usage Enforcement

The system now enforces daily limits:
1. **AI Call Processing**: Tracks actual speaking time with AI
2. **SMS Usage**: Tracks both incoming and outgoing SMS
3. **Daily Reset**: Limits reset at midnight each day
4. **Subscription-based**: Limits based on active subscription tier

## Migration Instructions

1. Run the migration: `004_update_subscription_tiers.sql`
2. Restart the backend service
3. Update frontend if needed
4. Test the new subscription system

## Testing

Use the provided test script:
```bash
python test_subscription_update.py
```

This will verify:
- New subscription tiers are created
- Database tables exist
- Usage tracking service works
- API endpoints respond correctly

## Backward Compatibility

The system maintains backward compatibility:
- Old tier names still work
- USD pricing still available
- Existing subscriptions continue to work
- Legacy fields preserved

## Notes

- The system tracks actual AI speaking time, not just call count
- SMS limits include both incoming and outgoing messages
- Agentic functions access is tied to subscription status
- Unlimited tiers use 999999 as the limit value
- All pricing is monthly and in UZS