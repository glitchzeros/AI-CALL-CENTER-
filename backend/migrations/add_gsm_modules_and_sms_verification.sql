-- Migration: Add GSM modules and SMS verification tables
-- Date: 2025-06-08
-- Description: Add tables for GSM module management, payment sessions, and SMS verification

-- Add new columns to users table for login SMS verification
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS require_sms_login BOOLEAN DEFAULT TRUE,
ADD COLUMN IF NOT EXISTS login_sms_code VARCHAR(6),
ADD COLUMN IF NOT EXISTS login_sms_expires_at TIMESTAMP,
ADD COLUMN IF NOT EXISTS last_login_sms_at TIMESTAMP;

-- Create GSM modules table
CREATE TABLE IF NOT EXISTS gsm_modules (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    bank_card_number VARCHAR(20) UNIQUE NOT NULL,
    bank_name VARCHAR(100) NOT NULL,
    card_holder_name VARCHAR(100) NOT NULL,
    device_id VARCHAR(50) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    is_available BOOLEAN DEFAULT TRUE,
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    priority INTEGER DEFAULT 1,
    status VARCHAR(20) DEFAULT 'idle',
    last_error TEXT,
    error_count INTEGER DEFAULT 0
);

-- Create payment sessions table
CREATE TABLE IF NOT EXISTS payment_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    gsm_module_id INTEGER NOT NULL REFERENCES gsm_modules(id) ON DELETE CASCADE,
    subscription_tier VARCHAR(50) NOT NULL,
    amount_uzs INTEGER NOT NULL,
    amount_usd INTEGER NOT NULL,
    bank_card_number VARCHAR(20) NOT NULL,
    bank_name VARCHAR(100) NOT NULL,
    card_holder_name VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    confirmed_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    confirmation_sms TEXT,
    confirmation_amount INTEGER
);

-- Create SMS verification sessions table
CREATE TABLE IF NOT EXISTS sms_verification_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    phone_number VARCHAR(20) NOT NULL,
    verification_code VARCHAR(6) NOT NULL,
    gsm_module_id INTEGER REFERENCES gsm_modules(id) ON DELETE SET NULL,
    session_type VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    verified_at TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending',
    attempts INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    is_demo BOOLEAN DEFAULT FALSE,
    demo_code_shown BOOLEAN DEFAULT FALSE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_gsm_modules_phone_number ON gsm_modules(phone_number);
CREATE INDEX IF NOT EXISTS idx_gsm_modules_status ON gsm_modules(status);
CREATE INDEX IF NOT EXISTS idx_gsm_modules_available ON gsm_modules(is_available);
CREATE INDEX IF NOT EXISTS idx_payment_sessions_user_id ON payment_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_payment_sessions_status ON payment_sessions(status);
CREATE INDEX IF NOT EXISTS idx_payment_sessions_expires_at ON payment_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_sms_verification_user_id ON sms_verification_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sms_verification_status ON sms_verification_sessions(status);
CREATE INDEX IF NOT EXISTS idx_sms_verification_expires_at ON sms_verification_sessions(expires_at);

-- Insert some demo GSM modules for testing
INSERT INTO gsm_modules (phone_number, bank_card_number, bank_name, card_holder_name, description, priority) VALUES
('+998901234567', '8600123456789012', 'Uzcard', 'Demo Company 1', 'Demo GSM module for testing', 1),
('+998901234568', '8600123456789013', 'Humo', 'Demo Company 2', 'Demo GSM module for testing', 2),
('+998901234569', '8600123456789014', 'Visa', 'Demo Company 3', 'Demo GSM module for testing', 3)
ON CONFLICT (phone_number) DO NOTHING;

-- Update trigger for updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers for updated_at
DROP TRIGGER IF EXISTS update_gsm_modules_updated_at ON gsm_modules;
CREATE TRIGGER update_gsm_modules_updated_at 
    BEFORE UPDATE ON gsm_modules 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at 
    BEFORE UPDATE ON users 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();