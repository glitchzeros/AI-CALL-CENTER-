-- Admin Management Schema
-- Enhanced system for API key management, modem assignment, and system prompts

-- Gemini API Keys Management
CREATE TABLE IF NOT EXISTS gemini_api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    api_key VARCHAR(255) UNIQUE NOT NULL,
    key_type VARCHAR(20) NOT NULL CHECK (key_type IN ('company', 'client')),
    status VARCHAR(20) DEFAULT 'available' CHECK (status IN ('available', 'assigned', 'expired', 'disabled')),
    assigned_to UUID REFERENCES users(id) ON DELETE SET NULL,
    assigned_at TIMESTAMP,
    expires_at TIMESTAMP,
    usage_count INTEGER DEFAULT 0,
    daily_limit INTEGER DEFAULT 1000,
    monthly_limit INTEGER DEFAULT 30000,
    last_used_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

-- Company Number Configurations
CREATE TABLE IF NOT EXISTS company_number_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_number VARCHAR(50) UNIQUE NOT NULL,
    system_prompt TEXT NOT NULL,
    ai_personality VARCHAR(50) DEFAULT 'professional',
    voice_settings JSONB DEFAULT '{}',
    gemini_api_key_id UUID REFERENCES gemini_api_keys(id) ON DELETE SET NULL,
    modem_assignment_id UUID,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- GSM Modem Management
CREATE TABLE IF NOT EXISTS gsm_modems (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    device_path VARCHAR(255) UNIQUE NOT NULL,
    device_name VARCHAR(255),
    usb_port VARCHAR(50),
    phone_number VARCHAR(20),
    imei VARCHAR(20),
    sim_card_id VARCHAR(50),
    carrier VARCHAR(100),
    signal_strength INTEGER,
    status VARCHAR(20) DEFAULT 'offline' CHECK (status IN ('online', 'offline', 'busy', 'error', 'maintenance')),
    role_type VARCHAR(20) DEFAULT 'unassigned' CHECK (role_type IN ('company_number', 'client_number', 'unassigned')),
    assigned_to_company VARCHAR(50),
    audio_device VARCHAR(255),
    configuration JSONB DEFAULT '{}',
    last_seen_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Client API Key Assignments (for subscription management)
CREATE TABLE IF NOT EXISTS client_api_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    gemini_api_key_id UUID REFERENCES gemini_api_keys(id) ON DELETE SET NULL,
    subscription_start TIMESTAMP NOT NULL,
    subscription_end TIMESTAMP NOT NULL,
    auto_renew BOOLEAN DEFAULT FALSE,
    usage_stats JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- API Key Usage Tracking
CREATE TABLE IF NOT EXISTS api_key_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    api_key_id UUID REFERENCES gemini_api_keys(id) ON DELETE CASCADE,
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    company_number VARCHAR(50),
    request_type VARCHAR(50),
    tokens_used INTEGER DEFAULT 0,
    response_time_ms INTEGER,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Admin Users
CREATE TABLE IF NOT EXISTS admin_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    admin_level VARCHAR(20) DEFAULT 'admin' CHECK (admin_level IN ('super_admin', 'admin', 'moderator')),
    permissions JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID REFERENCES users(id)
);

-- Add foreign key constraint for modem assignment
ALTER TABLE company_number_configs 
ADD CONSTRAINT fk_modem_assignment 
FOREIGN KEY (modem_assignment_id) REFERENCES gsm_modems(id) ON DELETE SET NULL;

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_gemini_api_keys_status ON gemini_api_keys(status);
CREATE INDEX IF NOT EXISTS idx_gemini_api_keys_type ON gemini_api_keys(key_type);
CREATE INDEX IF NOT EXISTS idx_gemini_api_keys_assigned_to ON gemini_api_keys(assigned_to);
CREATE INDEX IF NOT EXISTS idx_gemini_api_keys_expires_at ON gemini_api_keys(expires_at);

CREATE INDEX IF NOT EXISTS idx_company_number_configs_number ON company_number_configs(company_number);
CREATE INDEX IF NOT EXISTS idx_company_number_configs_active ON company_number_configs(is_active);

CREATE INDEX IF NOT EXISTS idx_gsm_modems_device_path ON gsm_modems(device_path);
CREATE INDEX IF NOT EXISTS idx_gsm_modems_status ON gsm_modems(status);
CREATE INDEX IF NOT EXISTS idx_gsm_modems_role_type ON gsm_modems(role_type);
CREATE INDEX IF NOT EXISTS idx_gsm_modems_phone_number ON gsm_modems(phone_number);

CREATE INDEX IF NOT EXISTS idx_client_api_assignments_user_id ON client_api_assignments(user_id);
CREATE INDEX IF NOT EXISTS idx_client_api_assignments_subscription_end ON client_api_assignments(subscription_end);

CREATE INDEX IF NOT EXISTS idx_api_key_usage_api_key_id ON api_key_usage(api_key_id);
CREATE INDEX IF NOT EXISTS idx_api_key_usage_timestamp ON api_key_usage(timestamp);
CREATE INDEX IF NOT EXISTS idx_api_key_usage_user_id ON api_key_usage(user_id);

-- Create triggers for updated_at timestamps
CREATE TRIGGER update_gemini_api_keys_updated_at BEFORE UPDATE ON gemini_api_keys
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_company_number_configs_updated_at BEFORE UPDATE ON company_number_configs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_gsm_modems_updated_at BEFORE UPDATE ON gsm_modems
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_client_api_assignments_updated_at BEFORE UPDATE ON client_api_assignments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create views for admin dashboard
CREATE OR REPLACE VIEW admin_dashboard_stats AS
SELECT 
    (SELECT COUNT(*) FROM gemini_api_keys WHERE status = 'available' AND key_type = 'client') as available_client_keys,
    (SELECT COUNT(*) FROM gemini_api_keys WHERE status = 'assigned' AND key_type = 'client') as assigned_client_keys,
    (SELECT COUNT(*) FROM gemini_api_keys WHERE key_type = 'company') as company_keys,
    (SELECT COUNT(*) FROM gsm_modems WHERE status = 'online') as online_modems,
    (SELECT COUNT(*) FROM gsm_modems WHERE role_type = 'unassigned') as unassigned_modems,
    (SELECT COUNT(*) FROM users WHERE subscription_status = 'active') as active_subscribers,
    (SELECT COUNT(*) FROM client_api_assignments WHERE subscription_end > CURRENT_TIMESTAMP) as active_api_assignments;

CREATE OR REPLACE VIEW modem_assignments_view AS
SELECT 
    m.id,
    m.device_path,
    m.device_name,
    m.usb_port,
    m.phone_number,
    m.status,
    m.role_type,
    m.assigned_to_company,
    cnc.system_prompt,
    gak.api_key as assigned_api_key,
    m.signal_strength,
    m.last_seen_at
FROM gsm_modems m
LEFT JOIN company_number_configs cnc ON m.id = cnc.modem_assignment_id
LEFT JOIN gemini_api_keys gak ON cnc.gemini_api_key_id = gak.id;

CREATE OR REPLACE VIEW api_key_assignments_view AS
SELECT 
    caa.id,
    u.email,
    u.company_number,
    gak.api_key,
    gak.status as key_status,
    caa.subscription_start,
    caa.subscription_end,
    caa.auto_renew,
    gak.usage_count,
    gak.daily_limit,
    gak.monthly_limit,
    CASE 
        WHEN caa.subscription_end < CURRENT_TIMESTAMP THEN 'expired'
        WHEN caa.subscription_end < CURRENT_TIMESTAMP + INTERVAL '7 days' THEN 'expiring_soon'
        ELSE 'active'
    END as subscription_status
FROM client_api_assignments caa
JOIN users u ON caa.user_id = u.id
JOIN gemini_api_keys gak ON caa.gemini_api_key_id = gak.id;

-- Insert default admin user (update with actual admin user ID)
-- INSERT INTO admin_users (user_id, admin_level, permissions) 
-- VALUES ('admin-user-uuid-here', 'super_admin', '{"all": true}');

-- Sample data for testing
INSERT INTO gemini_api_keys (api_key, key_type, status) VALUES 
('AIzaSyCompanyKey1_STATIC_COMPANY_USE', 'company', 'available'),
('AIzaSyCompanyKey2_STATIC_COMPANY_USE', 'company', 'available'),
('AIzaSyClientKey1_FOR_PAID_SUBSCRIBERS', 'client', 'available'),
('AIzaSyClientKey2_FOR_PAID_SUBSCRIBERS', 'client', 'available'),
('AIzaSyClientKey3_FOR_PAID_SUBSCRIBERS', 'client', 'available'),
('AIzaSyClientKey4_FOR_PAID_SUBSCRIBERS', 'client', 'available'),
('AIzaSyClientKey5_FOR_PAID_SUBSCRIBERS', 'client', 'available');

-- Sample company number configurations
INSERT INTO company_number_configs (company_number, system_prompt, ai_personality) VALUES 
('1000', 'You are a professional customer service AI assistant. Be helpful, polite, and efficient in your responses.', 'professional'),
('1001', 'You are a technical support AI specialist. Help users with technical issues and provide clear solutions.', 'technical'),
('1002', 'You are a sales AI assistant. Be enthusiastic and help customers find the right products or services.', 'sales');