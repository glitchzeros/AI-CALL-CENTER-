-- Initial Database Schema for Aetherium
-- The Scribe's Foundation

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_code VARCHAR(10),
    verification_expires_at TIMESTAMP,
    company_number VARCHAR(50) UNIQUE,
    subscription_tier VARCHAR(20) DEFAULT 'apprentice',
    subscription_status VARCHAR(20) DEFAULT 'inactive',
    subscription_start_date TIMESTAMP,
    subscription_end_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_type VARCHAR(20) NOT NULL, -- 'voice', 'sms', 'telegram'
    status VARCHAR(20) DEFAULT 'active', -- 'active', 'completed', 'failed'
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    duration INTEGER, -- in seconds
    phone_number VARCHAR(20),
    telegram_chat_id VARCHAR(50),
    conversation_summary TEXT,
    outcome VARCHAR(20) DEFAULT 'neutral', -- 'positive', 'negative', 'neutral'
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Workflows table
CREATE TABLE IF NOT EXISTS workflows (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    nodes JSONB DEFAULT '[]',
    connections JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT FALSE,
    trigger_type VARCHAR(50),
    trigger_config JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Payments table
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'USD',
    status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'completed', 'failed', 'expired'
    payment_method VARCHAR(20) DEFAULT 'bank_transfer',
    transaction_id VARCHAR(255),
    bank_reference VARCHAR(255),
    expires_at TIMESTAMP,
    completed_at TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Company numbers table
CREATE TABLE IF NOT EXISTS company_numbers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    number VARCHAR(50) UNIQUE NOT NULL,
    is_assigned BOOLEAN DEFAULT FALSE,
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Telegram chats table
CREATE TABLE IF NOT EXISTS telegram_chats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    chat_id VARCHAR(50) UNIQUE NOT NULL,
    chat_type VARCHAR(20), -- 'private', 'group', 'supergroup', 'channel'
    title VARCHAR(255),
    username VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    linked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP
);

-- Dream journal entries table
CREATE TABLE IF NOT EXISTS dream_journal_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    analysis_date DATE NOT NULL,
    total_sessions INTEGER DEFAULT 0,
    positive_interactions INTEGER DEFAULT 0,
    negative_interactions INTEGER DEFAULT 0,
    common_patterns JSONB DEFAULT '[]',
    insights TEXT,
    recommendations JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Modem status table
CREATE TABLE IF NOT EXISTS modem_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    modem_id VARCHAR(50) UNIQUE NOT NULL,
    device_path VARCHAR(255),
    audio_device VARCHAR(255),
    status VARCHAR(20) DEFAULT 'offline', -- 'online', 'offline', 'busy', 'error'
    signal_strength INTEGER,
    network_operator VARCHAR(100),
    last_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Statistics cache table
CREATE TABLE IF NOT EXISTS statistics_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    cache_key VARCHAR(255) NOT NULL,
    cache_data JSONB NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit log table
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone);
CREATE INDEX IF NOT EXISTS idx_users_company_number ON users(company_number);
CREATE INDEX IF NOT EXISTS idx_users_subscription_status ON users(subscription_status);

CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
CREATE INDEX IF NOT EXISTS idx_sessions_session_type ON sessions(session_type);
CREATE INDEX IF NOT EXISTS idx_sessions_start_time ON sessions(start_time);
CREATE INDEX IF NOT EXISTS idx_sessions_outcome ON sessions(outcome);

CREATE INDEX IF NOT EXISTS idx_workflows_user_id ON workflows(user_id);
CREATE INDEX IF NOT EXISTS idx_workflows_is_active ON workflows(is_active);

CREATE INDEX IF NOT EXISTS idx_payments_user_id ON payments(user_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at);

CREATE INDEX IF NOT EXISTS idx_telegram_chats_user_id ON telegram_chats(user_id);
CREATE INDEX IF NOT EXISTS idx_telegram_chats_chat_id ON telegram_chats(chat_id);

CREATE INDEX IF NOT EXISTS idx_dream_journal_analysis_date ON dream_journal_entries(analysis_date);

CREATE INDEX IF NOT EXISTS idx_modem_status_modem_id ON modem_status(modem_id);
CREATE INDEX IF NOT EXISTS idx_modem_status_status ON modem_status(status);

CREATE INDEX IF NOT EXISTS idx_statistics_cache_user_id ON statistics_cache(user_id);
CREATE INDEX IF NOT EXISTS idx_statistics_cache_key ON statistics_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_statistics_cache_expires_at ON statistics_cache(expires_at);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON audit_logs(created_at);

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE ON sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON workflows
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_modem_status_updated_at BEFORE UPDATE ON modem_status
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert default company numbers (1000-9999)
INSERT INTO company_numbers (number)
SELECT LPAD(generate_series(1000, 9999)::text, 4, '0')
ON CONFLICT (number) DO NOTHING;

-- Create views for common queries
CREATE OR REPLACE VIEW user_statistics AS
SELECT 
    u.id,
    u.email,
    u.company_number,
    u.subscription_tier,
    u.subscription_status,
    COUNT(s.id) as total_sessions,
    COUNT(CASE WHEN s.outcome = 'positive' THEN 1 END) as positive_sessions,
    COUNT(CASE WHEN s.outcome = 'negative' THEN 1 END) as negative_sessions,
    COUNT(CASE WHEN s.outcome = 'neutral' THEN 1 END) as neutral_sessions,
    COALESCE(SUM(s.duration), 0) as total_duration,
    MAX(s.start_time) as last_session_at
FROM users u
LEFT JOIN sessions s ON u.id = s.user_id
GROUP BY u.id, u.email, u.company_number, u.subscription_tier, u.subscription_status;

CREATE OR REPLACE VIEW active_sessions AS
SELECT 
    s.*,
    u.email,
    u.company_number,
    u.subscription_tier
FROM sessions s
JOIN users u ON s.user_id = u.id
WHERE s.status = 'active';

CREATE OR REPLACE VIEW payment_summary AS
SELECT 
    p.*,
    u.email,
    u.company_number
FROM payments p
JOIN users u ON p.user_id = u.id
ORDER BY p.created_at DESC;