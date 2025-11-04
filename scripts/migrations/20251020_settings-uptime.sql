-- Ensure success/error counters exist for API metrics
ALTER TABLE api_request_metrics
  ADD COLUMN IF NOT EXISTS success_count INTEGER NOT NULL DEFAULT 0;

ALTER TABLE api_request_metrics
  ADD COLUMN IF NOT EXISTS error_count INTEGER NOT NULL DEFAULT 0;

UPDATE api_request_metrics
SET success_count = request_count
WHERE success_count = 0 AND error_count = 0;

-- Service health telemetry table
CREATE TABLE IF NOT EXISTS service_health_logs (
  id UUID PRIMARY KEY,
  service_name TEXT NOT NULL,
  status BOOLEAN NOT NULL,
  latency_ms INTEGER,
  checked_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_service_health_logs_service_checked
  ON service_health_logs (service_name, checked_at DESC);
