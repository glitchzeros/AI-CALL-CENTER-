--
-- Aetherium Database Initialization Script
-- The Scribe's Foundational Parchment
-- This script creates all necessary tables and seeds initial data.
--

-- Enable extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users Table
-- Stores user account and authentication information.
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    company_number VARCHAR(20) UNIQUE,
    is_verified BOOLEAN DEFAULT FALSE,
    sms_verification_code VARCHAR(6),
    sms_verification_expires_at TIMESTAMP,
    require_sms_login BOOLEAN DEFAULT TRUE,
    login_sms_code VARCHAR(6),
    login_sms_expires_at TIMESTAMP,
    last_login_sms_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE users IS 'Stores user accounts and authentication credentials.';

-- Subscription Tiers Table
-- Defines the available subscription plans with their limits and pricing.
CREATE TABLE IF NOT EXISTS subscription_tiers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    description TEXT,
    price_usd FLOAT DEFAULT 0.0,
    price_uzs INTEGER DEFAULT 0,
    max_daily_ai_minutes INTEGER DEFAULT 240,
    max_daily_sms INTEGER DEFAULT 100,
    context_limit INTEGER DEFAULT 4000,
    has_agentic_functions BOOLEAN DEFAULT FALSE,
    has_agentic_constructor BOOLEAN DEFAULT FALSE,
    features TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE subscription_tiers IS 'Defines available subscription plans, features, and limits.';

-- User Subscriptions Table
-- Links users to their active subscription tier.
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tier_id INTEGER NOT NULL REFERENCES subscription_tiers(id),
    status VARCHAR(20) DEFAULT 'inactive',
    started_at TIMESTAMP,
    expires_at TIMESTAMP,
    auto_renew BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE user_subscriptions IS 'Tracks the subscription status for each user.';

-- User Daily Usage Table
-- Tracks daily resource consumption (AI minutes, SMS) for each user.
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
COMMENT ON TABLE user_daily_usage IS 'Tracks daily resource usage against subscription limits.';

-- Workflows Table
-- Stores the JSON definitions of user-created workflows.
CREATE TABLE IF NOT EXISTS scribe_workflows (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    workflow_data JSONB NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE scribe_workflows IS 'Stores user-created AI workflow definitions.';

-- Communication Sessions Table
-- Logs each voice, SMS, or Telegram session.
CREATE TABLE IF NOT EXISTS communication_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_type VARCHAR(20) NOT NULL,
    caller_id VARCHAR(50),
    company_number VARCHAR(20),
    status VARCHAR(20) DEFAULT 'active',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    duration_seconds INTEGER,
    outcome VARCHAR(20),
    ai_summary TEXT,
    context_data JSONB,
    current_invocation_state JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
COMMENT ON TABLE communication_sessions IS 'Main log for every communication session.';

-- Session Messages Table
-- Stores the transcript and messages for each communication session.
CREATE TABLE IF NOT EXISTS session_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER NOT NULL REFERENCES communication_sessions(id) ON DELETE CASCADE,
    speaker VARCHAR(10) NOT NULL,
    message_type VARCHAR(20) NOT NULL,
    content TEXT,
    audio_file_path VARCHAR(500),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);
COMMENT ON TABLE session_messages IS 'Stores individual messages within a communication session.';

-- Manual Payment Sessions Table
-- Tracks manual bank transfer payment attempts.
CREATE TABLE IF NOT EXISTS manual_payment_sessions (
    id SERIAL PRIMARY KEY,
    payment_id VARCHAR(100) UNIQUE NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    tier_name VARCHAR(50) NOT NULL,
    amount_usd DECIMAL(10, 2) NOT NULL,
    amount_uzs DECIMAL(12, 0) NOT NULL,
    reference_code VARCHAR(20) UNIQUE NOT NULL,
    company_number VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    confirmed_at TIMESTAMP,
    sms_content TEXT
);
COMMENT ON TABLE manual_payment_sessions IS 'Tracks manual bank transfer payment sessions.';


-- =========================
--      SEED INITIAL DATA
-- =========================

-- Seed Subscription Tiers with new structure
-- This uses ON CONFLICT to prevent errors on subsequent runs and allows for easy updates.
INSERT INTO subscription_tiers (name, display_name, description, price_usd, price_uzs, max_daily_ai_minutes, max_daily_sms, context_limit, has_agentic_functions, has_agentic_constructor, features) VALUES
('tier1', 'First Tier', 'Ideal for starting out and basic use cases.', 20, 250000, 240, 100, 4000, true, true, '["Basic AI Features", "Standard Support"]'),
('tier2', 'Second Tier', 'Perfect for growing businesses with higher demands.', 50, 750000, 480, 300, 32000, true, true, '["Advanced AI Features", "Priority Support", "Workflow Constructor"]'),
('tier3', 'Third Tier', 'Ultimate solution for large-scale enterprise needs.', 100, 1250000, 999999, 999999, -1, true, true, '["All Features", "Dedicated Support", "Unlimited Usage"]')
ON CONFLICT (name) DO UPDATE SET
    display_name = EXCLUDED.display_name,
    description = EXCLUDED.description,
    price_usd = EXCLUDED.price_usd,
    price_uzs = EXCLUDED.price_uzs,
    max_daily_ai_minutes = EXCLUDED.max_daily_ai_minutes,
    max_daily_sms = EXCLUDED.max_daily_sms,
    context_limit = EXCLUDED.context_limit,
    has_agentic_functions = EXCLUDED.has_agentic_functions,
    has_agentic_constructor = EXCLUDED.has_agentic_constructor,
    features = EXCLUDED.features,
    updated_at = CURRENT_TIMESTAMP;

-- =========================
--      CREATE INDEXES
-- =========================

-- Create indexes for performance improvements on frequently queried columns.
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON communication_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON session_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_workflows_user_id ON scribe_workflows(user_id);
CREATE INDEX IF NOT EXISTS idx_manual_payments_user_id ON manual_payment_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_manual_payments_reference_code ON manual_payment_sessions(reference_code);
CREATE INDEX IF NOT EXISTS idx_user_daily_usage_user_date ON user_daily_usage(user_id, usage_date);

-- Log completion to the console when the script finishes.
\echo '✅ Aetherium database initialized successfully with updated subscription tiers.'
