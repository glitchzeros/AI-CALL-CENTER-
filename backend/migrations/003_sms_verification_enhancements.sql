-- SMS Verification Enhancements Migration
-- Adds support for login SMS verification and GSM module management

-- Add login SMS verification fields to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS login_sms_code VARCHAR(6);
ALTER TABLE users ADD COLUMN IF NOT EXISTS login_sms_expires_at TIMESTAMP;
ALTER TABLE users ADD COLUMN IF NOT EXISTS login_requires_sms BOOLEAN DEFAULT FALSE;

-- Add bank card number to company number pool
ALTER TABLE company_number_pool ADD COLUMN IF NOT EXISTS bank_card_number VARCHAR(20);
ALTER TABLE company_number_pool ADD COLUMN IF NOT EXISTS bank_card_holder_name VARCHAR(255);

-- Add demo mode flag to GSM modems
ALTER TABLE gsm_modems ADD COLUMN IF NOT EXISTS is_demo_mode BOOLEAN DEFAULT FALSE;
ALTER TABLE gsm_modems ADD COLUMN IF NOT EXISTS demo_sms_code VARCHAR(6);
ALTER TABLE gsm_modems ADD COLUMN IF NOT EXISTS bank_card_number VARCHAR(20);
ALTER TABLE gsm_modems ADD COLUMN IF NOT EXISTS bank_card_holder_name VARCHAR(255);

-- Create GSM module management table for admin operations
CREATE TABLE IF NOT EXISTS gsm_module_management (
    id SERIAL PRIMARY KEY,
    modem_id INTEGER REFERENCES gsm_modems(id) ON DELETE CASCADE,
    action_type VARCHAR(20) NOT NULL, -- create, update, delete, assign, unassign
    performed_by INTEGER REFERENCES users(id),
    action_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create payment monitoring sessions table
CREATE TABLE IF NOT EXISTS payment_monitoring_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    subscription_tier_id INTEGER REFERENCES subscription_tiers(id),
    company_number VARCHAR(20) NOT NULL,
    bank_card_number VARCHAR(20) NOT NULL,
    amount_usd DECIMAL(10,2) NOT NULL,
    amount_uzs DECIMAL(12,0) NOT NULL,
    reference_code VARCHAR(20) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'monitoring', -- monitoring, confirmed, expired, cancelled
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    confirmed_at TIMESTAMP,
    last_sms_check TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sms_content TEXT
);

-- Add indexes for new fields
CREATE INDEX IF NOT EXISTS idx_users_login_sms_expires ON users(login_sms_expires_at);
CREATE INDEX IF NOT EXISTS idx_gsm_modems_demo_mode ON gsm_modems(is_demo_mode);
CREATE INDEX IF NOT EXISTS idx_payment_monitoring_status ON payment_monitoring_sessions(status);
CREATE INDEX IF NOT EXISTS idx_payment_monitoring_expires ON payment_monitoring_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_payment_monitoring_company ON payment_monitoring_sessions(company_number);

-- Insert some demo GSM modems if none exist
INSERT INTO gsm_modems (device_id, phone_number, status, is_demo_mode, demo_sms_code, bank_card_number, bank_card_holder_name)
SELECT 
    'DEMO_' || generate_random_uuid()::text,
    '+998901234' || (500 + row_number() OVER ())::text,
    'idle',
    true,
    LPAD((RANDOM() * 999999)::int::text, 6, '0'),
    '8600' || LPAD((RANDOM() * 999999999999)::bigint::text, 12, '0'),
    'Demo Company ' || row_number() OVER ()
FROM generate_series(1, 5)
WHERE NOT EXISTS (SELECT 1 FROM gsm_modems WHERE is_demo_mode = true);

-- Update company number pool with demo bank card numbers
UPDATE company_number_pool 
SET 
    bank_card_number = '8600' || LPAD((RANDOM() * 999999999999)::bigint::text, 12, '0'),
    bank_card_holder_name = 'Company ' || id
WHERE bank_card_number IS NULL;