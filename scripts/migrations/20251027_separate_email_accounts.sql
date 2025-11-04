-- Introduce dedicated email account storage decoupled from portal login
CREATE TABLE IF NOT EXISTS email_accounts (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  provider TEXT NOT NULL,
  email_address TEXT NOT NULL,
  display_name TEXT,
  login_email_snapshot TEXT,
  link_source TEXT NOT NULL DEFAULT 'oauth',
  refresh_token_encrypted TEXT NOT NULL,
  scopes TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
  is_primary BOOLEAN NOT NULL DEFAULT FALSE,
  oauth_consent BOOLEAN NOT NULL DEFAULT FALSE,
  ai_read_consent BOOLEAN NOT NULL DEFAULT FALSE,
  draft_only_mode BOOLEAN NOT NULL DEFAULT TRUE,
  consent_timestamp TIMESTAMP WITH TIME ZONE,
  ai_consent_revoked_at TIMESTAMP WITH TIME ZONE,
  last_consent_update TIMESTAMP WITH TIME ZONE,
  linked_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  last_connected_at TIMESTAMP WITH TIME ZONE,
  revoked_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  CONSTRAINT email_accounts_link_source_check CHECK (link_source IN ('oauth', 'migration', 'manual', 'legacy', 'login')),
  UNIQUE (user_id, email_address)
);
CREATE INDEX IF NOT EXISTS idx_email_accounts_user ON email_accounts(user_id);
CREATE INDEX IF NOT EXISTS idx_email_accounts_active ON email_accounts(user_id, revoked_at);

CREATE TABLE IF NOT EXISTS user_email_preferences (
  user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  active_account_id UUID REFERENCES email_accounts(id) ON DELETE SET NULL,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE OR REPLACE FUNCTION enforce_email_account_independence()
RETURNS TRIGGER AS $$
DECLARE
  login_email TEXT;
  effective_source TEXT;
BEGIN
  SELECT LOWER(email) INTO login_email FROM users WHERE id = NEW.user_id;
  effective_source := LOWER(COALESCE(NEW.link_source, 'oauth'));
  IF login_email IS NULL THEN
    RETURN NEW;
  END IF;
  IF LOWER(NEW.email_address) = login_email AND effective_source NOT IN ('legacy', 'login') THEN
    RAISE EXCEPTION USING MESSAGE = 'Linked email account must differ from portal login email.';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_email_account_independence ON email_accounts;
CREATE TRIGGER trg_email_account_independence
BEFORE INSERT OR UPDATE ON email_accounts
FOR EACH ROW EXECUTE FUNCTION enforce_email_account_independence();
