-- Aetherium Database Schema
-- The Scribe's Memory Palace

-- Users table for client accounts
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    company_number VARCHAR(20) UNIQUE,
    is_verified BOOLEAN DEFAULT FALSE,
    sms_verification_code VARCHAR(6),
    sms_verification_expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Subscription tiers and user subscriptions
CREATE TABLE subscription_tiers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    price_usd DECIMAL(10,2) NOT NULL,
    context_limit INTEGER NOT NULL, -- Token limit for conversation context
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default subscription tiers (with UZS pricing)
INSERT INTO subscription_tiers (name, price_usd, context_limit, description) VALUES
('Apprentice', 20.00, 4000, 'Context Memory: Up to 4,000 Tokens (Approx. 5 mins) | 246,000 so''m/oy'),
('Journeyman', 50.00, 32000, 'Context Memory: Up to 32,000 Tokens (Approx. 1 hour) | 615,000 so''m/oy'),
('Master Scribe', 100.00, -1, 'Context Memory: Full Session History (Unlimited Tokens) | 1,230,000 so''m/oy');

CREATE TABLE user_subscriptions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    tier_id INTEGER REFERENCES subscription_tiers(id),
    status VARCHAR(20) DEFAULT 'pending', -- pending, active, expired, cancelled
    started_at TIMESTAMP,
    expires_at TIMESTAMP,
    click_trans_id BIGINT,
    click_merchant_trans_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Scribe workflow configurations (The Invocation Editor saves)
CREATE TABLE scribe_workflows (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    workflow_data JSONB NOT NULL, -- Serialized workflow nodes and connections
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Communication sessions (calls, SMS, Telegram)
CREATE TABLE communication_sessions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    session_type VARCHAR(20) NOT NULL, -- voice, sms, telegram
    caller_id VARCHAR(50), -- Phone number or Telegram handle
    company_number VARCHAR(20), -- The assigned company number
    status VARCHAR(20) DEFAULT 'active', -- active, completed, failed, abandoned
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    duration_seconds INTEGER,
    outcome VARCHAR(20), -- positive, negative, neutral
    ai_summary TEXT,
    context_data JSONB, -- Conversation history and context
    current_invocation_state JSONB, -- Current workflow state
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Individual messages/interactions within sessions
CREATE TABLE session_messages (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES communication_sessions(id) ON DELETE CASCADE,
    speaker VARCHAR(10) NOT NULL, -- user, ai
    message_type VARCHAR(20) NOT NULL, -- text, audio, sms
    content TEXT,
    audio_file_path VARCHAR(500),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB -- Additional data like audio features, language detected, etc.
);

-- Call statistics and analytics
CREATE TABLE call_statistics (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    total_calls INTEGER DEFAULT 0,
    total_duration_seconds INTEGER DEFAULT 0,
    positive_interactions INTEGER DEFAULT 0,
    negative_interactions INTEGER DEFAULT 0,
    total_sms_sent INTEGER DEFAULT 0,
    total_sms_received INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);

-- The Scribe's Dream Journal (autonomous meta-analysis)
CREATE TABLE scribe_dream_journal (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    insight_category VARCHAR(50) NOT NULL, -- workflow_friction, potential_feature, performance_observation, etc.
    insight_summary TEXT NOT NULL,
    related_invocations TEXT[], -- Array of relevant Invocation types
    anonymized_example_snippet TEXT,
    severity_level VARCHAR(10) DEFAULT 'low', -- low, medium, high
    metadata JSONB -- Additional structured insights
);

-- GSM Modem management
CREATE TABLE gsm_modems (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR(50) UNIQUE NOT NULL, -- Physical device identifier
    control_port VARCHAR(50), -- /dev/ttyUSBX for AT commands
    audio_port VARCHAR(50), -- /dev/snd/pcmCYDX for audio
    phone_number VARCHAR(20) UNIQUE,
    status VARCHAR(20) DEFAULT 'offline', -- offline, idle, busy, error
    signal_strength INTEGER,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- SMS message queue and history
CREATE TABLE sms_messages (
    id SERIAL PRIMARY KEY,
    modem_id INTEGER REFERENCES gsm_modems(id),
    direction VARCHAR(10) NOT NULL, -- incoming, outgoing
    from_number VARCHAR(20),
    to_number VARCHAR(20),
    content TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, sent, delivered, failed
    session_id INTEGER REFERENCES communication_sessions(id),
    sent_at TIMESTAMP,
    received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB
);

-- Payment tracking for Click API integration
CREATE TABLE payment_transactions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    subscription_id INTEGER REFERENCES user_subscriptions(id),
    click_trans_id BIGINT UNIQUE,
    click_paydoc_id BIGINT,
    merchant_trans_id VARCHAR(255),
    merchant_prepare_id INTEGER,
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, completed, failed, cancelled
    error_code INTEGER,
    error_note TEXT,
    sign_time TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Manual payment sessions table for bank transfer payments
CREATE TABLE manual_payment_sessions (
    id SERIAL PRIMARY KEY,
    payment_id VARCHAR(100) UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    tier_name VARCHAR(50) NOT NULL,
    amount_usd DECIMAL(10,2) NOT NULL,
    amount_uzs DECIMAL(12,0) NOT NULL,
    reference_code VARCHAR(20) UNIQUE NOT NULL,
    company_number VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, confirmed, expired, cancelled
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    confirmed_at TIMESTAMP,
    sms_content TEXT
);

-- Telegram bot integration
CREATE TABLE telegram_chats (
    id SERIAL PRIMARY KEY,
    chat_id BIGINT UNIQUE NOT NULL,
    user_id INTEGER REFERENCES users(id),
    username VARCHAR(255),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Company number pool management
CREATE TABLE company_number_pool (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    is_assigned BOOLEAN DEFAULT FALSE,
    assigned_user_id INTEGER REFERENCES users(id),
    assigned_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone_number);
CREATE INDEX idx_users_company_number ON users(company_number);
CREATE INDEX idx_sessions_user_id ON communication_sessions(user_id);
CREATE INDEX idx_sessions_status ON communication_sessions(status);
CREATE INDEX idx_sessions_started_at ON communication_sessions(started_at);
CREATE INDEX idx_messages_session_id ON session_messages(session_id);
CREATE INDEX idx_messages_timestamp ON session_messages(timestamp);
CREATE INDEX idx_statistics_user_date ON call_statistics(user_id, date);
CREATE INDEX idx_modems_status ON gsm_modems(status);
CREATE INDEX idx_sms_direction_status ON sms_messages(direction, status);
CREATE INDEX idx_payments_click_trans_id ON payment_transactions(click_trans_id);
CREATE INDEX idx_manual_payments_reference ON manual_payment_sessions(reference_code);
CREATE INDEX idx_manual_payments_user_status ON manual_payment_sessions(user_id, status);
CREATE INDEX idx_manual_payments_expires ON manual_payment_sessions(expires_at);
CREATE INDEX idx_dream_journal_category ON scribe_dream_journal(insight_category);
CREATE INDEX idx_dream_journal_timestamp ON scribe_dream_journal(timestamp);

-- Trigger to update updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON user_subscriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_workflows_updated_at BEFORE UPDATE ON scribe_workflows FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_statistics_updated_at BEFORE UPDATE ON call_statistics FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payment_transactions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample company numbers for the pool
INSERT INTO company_number_pool (phone_number) VALUES
('+998901234567'),
('+998901234568'),
('+998901234569'),
('+998901234570'),
('+998901234571'),
('+998901234572'),
('+998901234573'),
('+998901234574'),
('+998901234575'),
('+998901234576');

-- Create a function to assign company numbers
CREATE OR REPLACE FUNCTION assign_company_number(p_user_id INTEGER)
RETURNS VARCHAR(20) AS $$
DECLARE
    assigned_number VARCHAR(20);
BEGIN
    -- Get the first available number and assign it
    UPDATE company_number_pool 
    SET is_assigned = TRUE, 
        assigned_user_id = p_user_id, 
        assigned_at = CURRENT_TIMESTAMP
    WHERE id = (
        SELECT id FROM company_number_pool 
        WHERE is_assigned = FALSE 
        ORDER BY id LIMIT 1
    )
    RETURNING phone_number INTO assigned_number;
    
    -- Update the user record
    UPDATE users SET company_number = assigned_number WHERE id = p_user_id;
    
    RETURN assigned_number;
END;
$$ LANGUAGE plpgsql;