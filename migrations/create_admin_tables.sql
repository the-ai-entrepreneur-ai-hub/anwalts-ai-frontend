-- Migration: Create Admin Dashboard Database Schema
-- Created: 2025-11-02
-- Purpose: Create required tables for admin dashboard functionality
-- Tables: organization_settings, analytics_events, api_tokens, webhooks

-- ============================================================================
-- 1. ORGANIZATION SETTINGS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS organization_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- General Settings
    language VARCHAR(10) DEFAULT 'de',
    timezone VARCHAR(50) DEFAULT 'Europe/Berlin',
    
    -- Security Settings
    require_two_factor BOOLEAN DEFAULT false,
    enable_sso BOOLEAN DEFAULT false,
    password_min_length INTEGER DEFAULT 8,
    password_require_special BOOLEAN DEFAULT true,
    password_require_numbers BOOLEAN DEFAULT true,
    
    -- Notification Settings
    email_notifications BOOLEAN DEFAULT true,
    browser_notifications BOOLEAN DEFAULT false,
    ai_updates BOOLEAN DEFAULT true,
    
    -- AI Configuration
    ai_model VARCHAR(100) DEFAULT 'qwen_legal_q4_k_m',
    ai_creativity INTEGER DEFAULT 70 CHECK (ai_creativity >= 0 AND ai_creativity <= 100),
    auto_save BOOLEAN DEFAULT true,
    
    -- Audit Fields
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_by UUID REFERENCES users(id)
);

-- Create index on updated_at for efficient "most recent" queries
CREATE INDEX IF NOT EXISTS idx_org_settings_updated_at ON organization_settings(updated_at DESC);

-- Insert default organization settings if none exist
INSERT INTO organization_settings (
    language, timezone, require_two_factor, enable_sso,
    password_min_length, password_require_special, password_require_numbers,
    email_notifications, browser_notifications, ai_updates,
    ai_model, ai_creativity, auto_save
)
SELECT 
    'de', 'Europe/Berlin', false, false,
    8, true, true,
    true, false, true,
    'qwen_legal_q4_k_m', 70, true
WHERE NOT EXISTS (SELECT 1 FROM organization_settings);

-- ============================================================================
-- 2. ANALYTICS EVENTS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS analytics_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Event Information
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB,
    
    -- Context
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    session_id VARCHAR(255),
    ip_address INET,
    user_agent TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_analytics_events_type ON analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_analytics_events_created_at ON analytics_events(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analytics_events_user_id ON analytics_events(user_id);
CREATE INDEX IF NOT EXISTS idx_analytics_events_type_created ON analytics_events(event_type, created_at DESC);

-- ============================================================================
-- 3. API TOKENS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS api_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Token Information
    name VARCHAR(255) NOT NULL,
    token_hash VARCHAR(255) NOT NULL UNIQUE,
    last_four VARCHAR(4) NOT NULL,
    
    -- Permissions & Scope
    scopes TEXT[] DEFAULT ARRAY[]::TEXT[],
    
    -- Ownership
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Status & Expiry
    is_active BOOLEAN DEFAULT true,
    expires_at TIMESTAMP WITH TIME ZONE,
    revoked_at TIMESTAMP WITH TIME ZONE,
    revoked_by UUID REFERENCES users(id) ON DELETE SET NULL,
    revoked_reason TEXT,
    
    -- Usage Tracking
    last_used_at TIMESTAMP WITH TIME ZONE,
    usage_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_api_tokens_created_by ON api_tokens(created_by);
CREATE INDEX IF NOT EXISTS idx_api_tokens_revoked_at ON api_tokens(revoked_at) WHERE revoked_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_api_tokens_is_active ON api_tokens(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_api_tokens_token_hash ON api_tokens(token_hash);

-- ============================================================================
-- 4. WEBHOOKS TABLE
-- ============================================================================
CREATE TABLE IF NOT EXISTS webhooks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Webhook Configuration
    name VARCHAR(255) NOT NULL,
    url TEXT NOT NULL,
    secret VARCHAR(255),
    
    -- Event Subscriptions
    events TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
    
    -- Status
    is_active BOOLEAN DEFAULT true,
    
    -- Ownership
    created_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Delivery Settings
    retry_on_failure BOOLEAN DEFAULT true,
    max_retries INTEGER DEFAULT 3,
    timeout_seconds INTEGER DEFAULT 30,
    
    -- Statistics
    last_triggered_at TIMESTAMP WITH TIME ZONE,
    last_success_at TIMESTAMP WITH TIME ZONE,
    last_failure_at TIMESTAMP WITH TIME ZONE,
    success_count INTEGER DEFAULT 0,
    failure_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_webhooks_created_by ON webhooks(created_by);
CREATE INDEX IF NOT EXISTS idx_webhooks_is_active ON webhooks(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_webhooks_events ON webhooks USING GIN(events);

-- ============================================================================
-- 5. WEBHOOK LOGS TABLE (for tracking deliveries)
-- ============================================================================
CREATE TABLE IF NOT EXISTS webhook_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Reference
    webhook_id UUID NOT NULL REFERENCES webhooks(id) ON DELETE CASCADE,
    
    -- Delivery Information
    event_type VARCHAR(100) NOT NULL,
    payload JSONB,
    
    -- Response
    http_status INTEGER,
    response_body TEXT,
    response_time_ms INTEGER,
    
    -- Status
    success BOOLEAN NOT NULL,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Timestamp
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_webhook_logs_webhook_id ON webhook_logs(webhook_id);
CREATE INDEX IF NOT EXISTS idx_webhook_logs_created_at ON webhook_logs(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_webhook_logs_success ON webhook_logs(success);

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify tables were created
SELECT 
    table_name,
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = t.table_name) as column_count
FROM information_schema.tables t
WHERE table_schema = 'public' 
  AND table_name IN ('organization_settings', 'analytics_events', 'api_tokens', 'webhooks', 'webhook_logs')
ORDER BY table_name;

-- Verify default organization settings
SELECT 
    id, 
    language, 
    timezone, 
    ai_model, 
    ai_creativity, 
    created_at 
FROM organization_settings 
ORDER BY created_at DESC 
LIMIT 1;

-- Show index count per table
SELECT 
    tablename,
    COUNT(*) as index_count
FROM pg_indexes
WHERE schemaname = 'public'
  AND tablename IN ('organization_settings', 'analytics_events', 'api_tokens', 'webhooks', 'webhook_logs')
GROUP BY tablename
ORDER BY tablename;

-- Migration complete message
SELECT 'Admin database schema migration completed successfully!' as status;
