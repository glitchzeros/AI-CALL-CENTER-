-- Update Subscription Tiers Migration
-- Version: 004
-- Description: Add new fields for UZS pricing and daily limits, update subscription tiers

-- Add new columns to subscription_tiers table
ALTER TABLE subscription_tiers ADD COLUMN IF NOT EXISTS price_usd DECIMAL(10,2) DEFAULT 0.0;
ALTER TABLE subscription_tiers ADD COLUMN IF NOT EXISTS price_uzs INTEGER DEFAULT 0;
ALTER TABLE subscription_tiers ADD COLUMN IF NOT EXISTS max_daily_ai_minutes INTEGER DEFAULT 240;
ALTER TABLE subscription_tiers ADD COLUMN IF NOT EXISTS max_daily_sms INTEGER DEFAULT 100;
ALTER TABLE subscription_tiers ADD COLUMN IF NOT EXISTS context_limit INTEGER DEFAULT 1000;
ALTER TABLE subscription_tiers ADD COLUMN IF NOT EXISTS has_agentic_functions BOOLEAN DEFAULT FALSE;
ALTER TABLE subscription_tiers ADD COLUMN IF NOT EXISTS has_agentic_constructor BOOLEAN DEFAULT FALSE;

-- Update existing tiers or insert new ones
-- First, delete existing tiers to avoid conflicts
DELETE FROM subscription_tiers WHERE name IN ('free', 'basic', 'premium', 'enterprise');

-- Insert new subscription tiers according to requirements
INSERT INTO subscription_tiers (
    name, 
    display_name, 
    description, 
    price_monthly, 
    price_yearly, 
    price_usd, 
    price_uzs,
    max_sessions_per_month,
    max_session_duration_minutes,
    max_daily_ai_minutes,
    max_daily_sms,
    context_limit,
    has_agentic_functions,
    has_agentic_constructor,
    features,
    is_active
) VALUES
-- Tier 1: 250,000 UZS, 4 hours (240 minutes) AI processing, 100 SMS, agentic functions access
('tier1', 'First Tier', 
 'Basic tier with 4 hours daily AI call processing, 100 SMS per day, and agentic functions access', 
 20.33, 244.0, 20.33, 250000,
 100, 60, 240, 100, 2000, 
 true, true, 
 '["ai_call_processing", "sms_service", "agentic_functions", "agentic_constructor"]',
 true),

-- Tier 2: 750,000 UZS, 8 hours (480 minutes) AI processing, 300 SMS, everything from tier 1
('tier2', 'Second Tier', 
 'Enhanced tier with 8 hours daily AI call processing, 300 SMS per day, and all first tier features', 
 60.98, 732.0, 60.98, 750000,
 300, 120, 480, 300, 5000, 
 true, true, 
 '["ai_call_processing", "sms_service", "agentic_functions", "agentic_constructor", "enhanced_limits"]',
 true),

-- Tier 3: 1,250,000 UZS, unlimited minutes and SMS, everything from tier 1
('tier3', 'Third Tier', 
 'Premium tier with unlimited AI call processing, unlimited SMS, and all features', 
 101.63, 1220.0, 101.63, 1250000,
 999999, 999999, 999999, 999999, 10000, 
 true, true, 
 '["ai_call_processing", "sms_service", "agentic_functions", "agentic_constructor", "unlimited_usage", "priority_support"]',
 true)
ON CONFLICT (name) DO UPDATE SET
    display_name = EXCLUDED.display_name,
    description = EXCLUDED.description,
    price_monthly = EXCLUDED.price_monthly,
    price_yearly = EXCLUDED.price_yearly,
    price_usd = EXCLUDED.price_usd,
    price_uzs = EXCLUDED.price_uzs,
    max_sessions_per_month = EXCLUDED.max_sessions_per_month,
    max_session_duration_minutes = EXCLUDED.max_session_duration_minutes,
    max_daily_ai_minutes = EXCLUDED.max_daily_ai_minutes,
    max_daily_sms = EXCLUDED.max_daily_sms,
    context_limit = EXCLUDED.context_limit,
    has_agentic_functions = EXCLUDED.has_agentic_functions,
    has_agentic_constructor = EXCLUDED.has_agentic_constructor,
    features = EXCLUDED.features,
    is_active = EXCLUDED.is_active,
    updated_at = CURRENT_TIMESTAMP;

-- Create table for tracking daily usage limits
CREATE TABLE IF NOT EXISTS user_daily_usage (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    usage_date DATE NOT NULL,
    ai_minutes_used INTEGER DEFAULT 0,
    sms_count_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, usage_date)
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_subscription_tiers_price_uzs ON subscription_tiers(price_uzs);
CREATE INDEX IF NOT EXISTS idx_subscription_tiers_active ON subscription_tiers(is_active);
CREATE INDEX IF NOT EXISTS idx_user_daily_usage_user_date ON user_daily_usage(user_id, usage_date);
CREATE INDEX IF NOT EXISTS idx_user_daily_usage_date ON user_daily_usage(usage_date);

-- Add trigger for updating user_daily_usage updated_at
CREATE TRIGGER update_user_daily_usage_updated_at 
    BEFORE UPDATE ON user_daily_usage 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Update any existing user subscriptions to use tier1 by default
UPDATE user_subscriptions 
SET tier_id = (SELECT id FROM subscription_tiers WHERE name = 'tier1' LIMIT 1)
WHERE tier_id NOT IN (SELECT id FROM subscription_tiers WHERE name IN ('tier1', 'tier2', 'tier3'));