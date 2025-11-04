-- Settings admin overhaul migration
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE api_tokens ADD COLUMN IF NOT EXISTS last_used_at TIMESTAMP WITH TIME ZONE;

CREATE TABLE IF NOT EXISTS organization_settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  language TEXT NOT NULL DEFAULT 'de',
  timezone TEXT NOT NULL DEFAULT 'Europe/Berlin',
  require_two_factor BOOLEAN NOT NULL DEFAULT FALSE,
  enable_sso BOOLEAN NOT NULL DEFAULT FALSE,
  password_min_length BOOLEAN NOT NULL DEFAULT TRUE,
  password_require_special BOOLEAN NOT NULL DEFAULT TRUE,
  password_require_numbers BOOLEAN NOT NULL DEFAULT TRUE,
  email_notifications BOOLEAN NOT NULL DEFAULT TRUE,
  browser_notifications BOOLEAN NOT NULL DEFAULT FALSE,
  ai_updates BOOLEAN NOT NULL DEFAULT TRUE,
  ai_model TEXT DEFAULT 'qwen_legal_q4_k_m',
  ai_creativity INTEGER DEFAULT 70,
  auto_save BOOLEAN NOT NULL DEFAULT TRUE,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_by UUID REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS webhooks (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  url TEXT NOT NULL,
  events TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
  secret TEXT,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE,
  created_by UUID REFERENCES users(id)
);
CREATE INDEX IF NOT EXISTS idx_webhooks_active ON webhooks(is_active);

CREATE TABLE IF NOT EXISTS webhook_logs (
  id UUID PRIMARY KEY,
  webhook_id UUID NOT NULL REFERENCES webhooks(id) ON DELETE CASCADE,
  status_code INTEGER,
  latency_ms INTEGER,
  response_body TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  trace_id TEXT
);
CREATE INDEX IF NOT EXISTS idx_webhook_logs_webhook ON webhook_logs(webhook_id, created_at DESC);

CREATE TABLE IF NOT EXISTS api_request_metrics (
  bucket_start TIMESTAMP WITH TIME ZONE NOT NULL,
  method TEXT NOT NULL,
  path TEXT NOT NULL,
  request_count INTEGER NOT NULL DEFAULT 0,
  total_latency_ms BIGINT NOT NULL DEFAULT 0,
  max_latency_ms INTEGER NOT NULL DEFAULT 0,
  success_count INTEGER NOT NULL DEFAULT 0,
  error_count INTEGER NOT NULL DEFAULT 0,
  last_status INTEGER,
  last_seen_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  PRIMARY KEY (bucket_start, method, path)
);
CREATE INDEX IF NOT EXISTS idx_api_request_metrics_path ON api_request_metrics(path, bucket_start DESC);
