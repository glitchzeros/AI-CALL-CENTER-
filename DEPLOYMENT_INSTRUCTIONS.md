# Subscription System Update - Deployment Instructions

## Overview
This document provides step-by-step instructions for deploying the updated subscription system with UZS pricing and daily usage limits.

## Pre-Deployment Checklist

✅ All validations passed  
✅ Migration file created: `004_update_subscription_tiers.sql`  
✅ Backend code updated  
✅ Frontend code updated  
✅ Documentation complete  

## Deployment Steps

### 1. Database Migration

**IMPORTANT**: Backup your database before running the migration!

```bash
# Connect to your PostgreSQL database
psql -h your_host -U your_user -d aetherium

# Run the migration
\i backend/migrations/004_update_subscription_tiers.sql

# Verify the migration
SELECT name, display_name, price_uzs, max_daily_ai_minutes, max_daily_sms 
FROM subscription_tiers 
ORDER BY price_uzs;
```

Expected output:
```
   name   | display_name | price_uzs | max_daily_ai_minutes | max_daily_sms
----------+--------------+-----------+----------------------+---------------
 tier1    | First Tier   |    250000 |                  240 |           100
 tier2    | Second Tier  |    750000 |                  480 |           300
 tier3    | Third Tier   |   1250000 |               999999 |        999999
```

### 2. Backend Deployment

```bash
# Navigate to backend directory
cd backend/

# Install any new dependencies (if needed)
pip install -r requirements.txt

# Restart the backend service
# For Docker:
docker-compose restart backend

# For direct deployment:
python main.py
```

### 3. Frontend Deployment

```bash
# Navigate to frontend directory
cd frontend/

# Install dependencies (if needed)
npm install

# Build for production
npm run build

# Deploy the built files to your web server
# For Docker:
docker-compose restart frontend
```

### 4. Verification

#### 4.1 Check API Endpoints

Test the new endpoints:

```bash
# Get subscription tiers
curl -X GET "http://your-api-url/api/subscriptions/tiers" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get user subscription
curl -X GET "http://your-api-url/api/subscriptions/my-subscription" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get usage status
curl -X GET "http://your-api-url/api/subscriptions/usage-status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 4.2 Test AI Session Management

```bash
# Start AI session
curl -X POST "http://your-api-url/api/ai-sessions/start" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"session_type": "call_processing"}'

# Check session status
curl -X GET "http://your-api-url/api/ai-sessions/status/SESSION_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"

# End AI session
curl -X POST "http://your-api-url/api/ai-sessions/end" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "SESSION_ID"}'
```

#### 4.3 Frontend Verification

1. Navigate to the subscription page
2. Verify new pricing is displayed in UZS
3. Check that daily usage limits are shown
4. Confirm agentic functions access is displayed
5. Test subscription purchase flow

## New Features Available

### For Users

1. **UZS Pricing**: All subscription prices now displayed in Uzbek Som
2. **Daily Usage Tracking**: Real-time tracking of AI minutes and SMS usage
3. **Usage Limits**: Automatic enforcement of daily limits based on subscription tier
4. **Agentic Functions**: Access to advanced AI agent capabilities
5. **Usage Dashboard**: Visual representation of daily usage on subscription page

### For Developers

1. **Usage Tracking Service**: `UsageTrackingService` for monitoring usage
2. **AI Usage Middleware**: `AIUsageMiddleware` for session management
3. **New API Endpoints**: Enhanced subscription and usage management
4. **SMS Usage Integration**: Automatic SMS usage tracking
5. **Session Management**: AI session tracking and limit enforcement

## Configuration

### Environment Variables

No new environment variables are required. The system uses existing database connections.

### Feature Flags

The system automatically detects subscription tiers and applies appropriate limits:
- Unlimited tiers use 999999 as the limit value
- Usage tracking is enabled for all tiers
- Agentic functions access is tier-based

## Monitoring

### Key Metrics to Monitor

1. **Daily Usage Patterns**
   ```sql
   SELECT usage_date, 
          AVG(ai_minutes_used) as avg_ai_minutes,
          AVG(sms_count_used) as avg_sms_count
   FROM user_daily_usage 
   WHERE usage_date >= CURRENT_DATE - INTERVAL '7 days'
   GROUP BY usage_date
   ORDER BY usage_date;
   ```

2. **Subscription Distribution**
   ```sql
   SELECT st.name, st.display_name, COUNT(us.id) as user_count
   FROM subscription_tiers st
   LEFT JOIN user_subscriptions us ON st.id = us.tier_id AND us.status = 'active'
   GROUP BY st.id, st.name, st.display_name
   ORDER BY st.price_uzs;
   ```

3. **Usage Limit Violations**
   ```sql
   SELECT u.email, udu.usage_date, udu.ai_minutes_used, st.max_daily_ai_minutes
   FROM user_daily_usage udu
   JOIN users u ON udu.user_id = u.id
   JOIN user_subscriptions us ON u.id = us.user_id AND us.status = 'active'
   JOIN subscription_tiers st ON us.tier_id = st.id
   WHERE udu.ai_minutes_used > st.max_daily_ai_minutes
   AND st.max_daily_ai_minutes < 999999;
   ```

## Troubleshooting

### Common Issues

1. **Migration Fails**
   - Check database permissions
   - Ensure no active connections are blocking the migration
   - Verify PostgreSQL version compatibility

2. **Usage Tracking Not Working**
   - Check if `user_daily_usage` table exists
   - Verify database triggers are working
   - Check application logs for errors

3. **Frontend Not Showing New Features**
   - Clear browser cache
   - Verify API endpoints are responding
   - Check console for JavaScript errors

4. **SMS Usage Not Tracked**
   - Ensure SMS service is updated with new parameters
   - Check if `user_id` and `db_session` are passed to SMS functions
   - Verify usage tracking service is imported correctly

### Log Monitoring

Monitor these log patterns:

```bash
# AI session tracking
grep "AI session started\|AI session ended" /var/log/aetherium/backend.log

# SMS usage tracking
grep "SMS sent\|SMS blocked" /var/log/aetherium/backend.log

# Usage limit violations
grep "usage limit\|limit exceeded" /var/log/aetherium/backend.log
```

## Rollback Plan

If issues occur, you can rollback:

1. **Database Rollback**
   ```sql
   -- Remove new columns (if needed)
   ALTER TABLE subscription_tiers DROP COLUMN IF EXISTS price_uzs;
   ALTER TABLE subscription_tiers DROP COLUMN IF EXISTS max_daily_ai_minutes;
   ALTER TABLE subscription_tiers DROP COLUMN IF EXISTS max_daily_sms;
   ALTER TABLE subscription_tiers DROP COLUMN IF EXISTS has_agentic_functions;
   ALTER TABLE subscription_tiers DROP COLUMN IF EXISTS has_agentic_constructor;
   
   -- Drop new table
   DROP TABLE IF EXISTS user_daily_usage;
   ```

2. **Code Rollback**
   - Revert to previous Git commit
   - Redeploy previous version

## Support

For issues or questions:
1. Check the logs first
2. Review the troubleshooting section
3. Consult the `SUBSCRIPTION_UPDATE_SUMMARY.md` for technical details
4. Run the validation script: `python validate_subscription_system.py`

## Success Criteria

The deployment is successful when:
- ✅ All API endpoints respond correctly
- ✅ Frontend displays new pricing and features
- ✅ Usage tracking works for AI and SMS
- ✅ Subscription purchases work with UZS pricing
- ✅ Daily limits are enforced correctly
- ✅ No errors in application logs

---

**Deployment Date**: _To be filled when deployed_  
**Deployed By**: _To be filled when deployed_  
**Version**: 1.0.0 - Subscription System Update