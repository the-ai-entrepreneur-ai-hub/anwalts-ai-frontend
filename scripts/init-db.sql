-- Initial schema for Anwalts AI backend
CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  name TEXT NOT NULL,
  role TEXT NOT NULL DEFAULT 'assistant',
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  is_active BOOLEAN NOT NULL DEFAULT TRUE
);
ALTER TABLE users
  ADD COLUMN IF NOT EXISTS is_active BOOLEAN NOT NULL DEFAULT TRUE;

CREATE TABLE IF NOT EXISTS user_profiles (
  user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  data JSONB,
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS templates (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  category TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  updated_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS idx_templates_user ON templates(user_id);

CREATE TABLE IF NOT EXISTS clauses (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  category TEXT,
  language TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_clauses_user ON clauses(user_id);

CREATE TABLE IF NOT EXISTS clipboard_entries (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  type TEXT NOT NULL DEFAULT 'text',
  created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_clipboard_user ON clipboard_entries(user_id);

CREATE TABLE IF NOT EXISTS analytics_events (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id) ON DELETE SET NULL,
  event_type TEXT NOT NULL,
  data JSONB,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_user ON analytics_events(user_id);

CREATE TABLE IF NOT EXISTS documents (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  type TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_documents_user ON documents(user_id);

CREATE TABLE IF NOT EXISTS api_tokens (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash TEXT NOT NULL,
  last4 TEXT NOT NULL,
  expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  revoked_at TIMESTAMP WITH TIME ZONE,
  last_used_at TIMESTAMP WITH TIME ZONE
);
CREATE INDEX IF NOT EXISTS idx_tokens_user ON api_tokens(user_id);
CREATE INDEX IF NOT EXISTS idx_tokens_valid ON api_tokens(user_id, revoked_at);

ALTER TABLE api_tokens
  ADD COLUMN IF NOT EXISTS last_used_at TIMESTAMP WITH TIME ZONE;

CREATE TABLE IF NOT EXISTS call_requests (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  phone TEXT NOT NULL,
  email TEXT,
  message TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL
);

CREATE TABLE IF NOT EXISTS assistant_messages (
  id UUID PRIMARY KEY,
  conversation_id UUID,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  role TEXT NOT NULL,
  content TEXT NOT NULL,
  model TEXT,
  message_hash TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_assistant_messages_user ON assistant_messages(user_id);

-- Organization-wide settings
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

-- Outbound webhook registry
CREATE TABLE IF NOT EXISTS webhooks (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  url TEXT NOT NULL,
  events TEXT[] NOT NULL DEFAULT ARRAY[]::TEXT[],
  secret TEXT,
  is_active BOOLEAN NOT NULL DEFAULT TRUE,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
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
  created_at TIMESTAMP WITH TIME ZONE NOT NULL,
  trace_id TEXT
);
CREATE INDEX IF NOT EXISTS idx_webhook_logs_webhook ON webhook_logs(webhook_id, created_at DESC);

-- API request metrics (per minute buckets)
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

-- Email account linking (separate from portal authentication)
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

CREATE TABLE IF NOT EXISTS domain_email_accounts (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  email_address TEXT NOT NULL,
  host TEXT NOT NULL,
  port INTEGER NOT NULL DEFAULT 993,
  username TEXT NOT NULL,
  credential_encrypted TEXT NOT NULL,
  use_ssl BOOLEAN NOT NULL DEFAULT TRUE,
  protocol TEXT NOT NULL DEFAULT 'imap',
  mailbox_access_consent BOOLEAN NOT NULL DEFAULT FALSE,
  ai_read_consent BOOLEAN NOT NULL DEFAULT FALSE,
  last_verified_at TIMESTAMP WITH TIME ZONE,
  last_status TEXT,
  created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
  CONSTRAINT domain_email_accounts_protocol_chk CHECK (protocol IN ('imap', 'ews'))
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_domain_email_accounts_user_email ON domain_email_accounts(user_id, email_address);

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

-- Insert sample user for templates (if not exists)
INSERT INTO users (id, email, name, role, password_hash, created_at)
VALUES (
  '00000000-0000-0000-0000-000000000001',
  'system@anwalts.ai',
  'System',
  'admin',
  'no-login',
  NOW()
) ON CONFLICT (email) DO NOTHING;

-- Insert sample templates
INSERT INTO templates (id, user_id, title, content, category, created_at, updated_at) VALUES
(
  gen_random_uuid(),
  '00000000-0000-0000-0000-000000000001',
  'NDA – Standard (DE)',
  E'# GEHEIMHALTUNGSVEREINBARUNG\n\nZwischen:\n\n[Unternehmensname], vertreten durch [Vertreter]\n[Adresse]\n\nund\n\n[Unternehmensname], vertreten durch [Vertreter]\n[Adresse]\n\nwird folgende Geheimhaltungsvereinbarung geschlossen:\n\n## § 1 Gegenstand\nDie Parteien beabsichtigen eine geschäftliche Zusammenarbeit. Zu diesem Zweck werden vertrauliche Informationen ausgetauscht.\n\n## § 2 Vertraulichkeit\nAlle ausgetauschten Informationen sind als vertraulich zu behandeln und dürfen ohne vorherige schriftliche Zustimmung nicht an Dritte weitergegeben werden.\n\n## § 3 Laufzeit\nDiese Vereinbarung gilt für einen Zeitraum von [2] Jahren ab Unterzeichnung.',
  'Vertrag',
  NOW() - INTERVAL '12 days',
  NOW() - INTERVAL '12 days'
),
(
  gen_random_uuid(),
  '00000000-0000-0000-0000-000000000001',
  'Klageentwurf – Zivilrecht',
  E'# KLAGE\n\nAn das [Amtsgericht/Landgericht] [Ort]\n\nIn Sachen:\n\n[Kläger Name]\n[Adresse]\n- Kläger -\n\nProzessbevollmächtigter: [Rechtsanwalt]\n\ngegen\n\n[Beklagter Name]\n[Adresse]\n- Beklagter -\n\nwegen: [Forderung/Anspruch]\n\nStreitwert: [Betrag] EUR\n\n## ANTRAG\n\nDer Beklagte wird verurteilt, an den Kläger [Betrag] EUR nebst Zinsen in Höhe von 5 Prozentpunkten über dem Basiszinssatz seit [Datum] zu zahlen.\n\n## BEGRÜNDUNG\n\nI. Sachverhalt\n[Sachverhalt darstellen]\n\nII. Rechtliche Würdigung\n[Rechtliche Begründung]',
  'Zivilrecht',
  NOW() - INTERVAL '30 days',
  NOW() - INTERVAL '30 days'
),
(
  gen_random_uuid(),
  '00000000-0000-0000-0000-000000000001',
  'Vollmacht – Mandanten',
  E'# VOLLMACHT\n\nIch/Wir erteile(n) hiermit\n\n[Rechtsanwalt/Kanzlei]\n[Adresse]\n\nVollmacht zur Vertretung meiner/unserer Interessen in der Angelegenheit:\n\n[Beschreibung der Angelegenheit]\n\nDie Vollmacht umfasst:\n\n- Entgegennahme und Übermittlung von Schriftstücken\n- Abgabe und Entgegennahme von Erklärungen\n- Vertretung vor Behörden und Gerichten\n- Abschluss von Vergleichen\n\nOrt, Datum: ________________\n\nUnterschrift Mandant: ________________',
  'Allgemein',
  NOW() - INTERVAL '10 days',
  NOW() - INTERVAL '10 days'
),
(
  gen_random_uuid(),
  '00000000-0000-0000-0000-000000000001',
  'Vergleichsangebot',
  E'# VERGLEICHSANGEBOT\n\nBezugnehmend auf das Verfahren [Az.: ...] unterbreite ich im Namen meines Mandanten folgendes Vergleichsangebot:\n\n## Vergleichsvorschlag\n\n1. Der Beklagte zahlt an den Kläger [Betrag] EUR.\n\n2. Die Zahlung erfolgt bis zum [Datum].\n\n3. Damit sind alle Ansprüche aus dem streitgegenständlichen Sachverhalt erledigt.\n\n4. Die Kosten des Rechtsstreits trägt jede Partei selbst.\n\n## Annahmefrist\n\nDieses Angebot gilt bis zum [Datum].\n\nMit freundlichen Grüßen\n\n[Rechtsanwalt]',
  'Zivilrecht',
  NOW() - INTERVAL '4 days',
  NOW() - INTERVAL '4 days'
),
(
  gen_random_uuid(),
  '00000000-0000-0000-0000-000000000001',
  'Abmahnung – Wettbewerbsrecht',
  E'# ABMAHNUNG WEGEN WETTBEWERBSVERSTOSS\n\nSehr geehrte Damen und Herren,\n\nim Namen und Auftrag unseres Mandanten, [Mandant], mahne ich Sie wegen wettbewerbswidriger Handlungen ab.\n\n## Sachverhalt\n\n[Beschreibung des Wettbewerbsverstoßes]\n\n## Rechtliche Bewertung\n\nDie dargestellten Handlungen verstoßen gegen § [Nummer] UWG.\n\n## Aufforderung\n\n1. Unterlassen Sie künftig [konkrete Handlung].\n\n2. Geben Sie bis zum [Datum] eine strafbewehrte Unterlassungserklärung ab.\n\n3. Erstatten Sie unsere Rechtsanwaltskosten in Höhe von [Betrag] EUR.\n\nMit freundlichen Grüßen\n\n[Rechtsanwalt]',
  'Wettbewerb',
  NOW() - INTERVAL '18 days',
  NOW() - INTERVAL '18 days'
),
(
  gen_random_uuid(),
  '00000000-0000-0000-0000-000000000001',
  'DSGVO – Auskunftsersuchen',
  E'# AUSKUNFTSERSUCHEN NACH ART. 15 DSGVO\n\nSehr geehrte Damen und Herren,\n\nhiermit fordere ich Sie gemäß Art. 15 DSGVO auf, mir Auskunft über die zu meiner Person gespeicherten Daten zu erteilen.\n\n## Geforderte Auskünfte\n\n1. Bestätigung, ob Sie personenbezogene Daten über mich verarbeiten\n\n2. Falls ja:\n   - Kategorien der verarbeiteten Daten\n   - Verarbeitungszwecke\n   - Empfänger oder Kategorien von Empfängern\n   - Geplante Speicherdauer\n   - Herkunft der Daten\n\n3. Kopie der verarbeiteten personenbezogenen Daten\n\nIch bitte um Beantwortung innerhalb der gesetzlichen Frist von einem Monat.\n\nMit freundlichen Grüßen\n\n[Name]',
  'Datenschutz',
  NOW() - INTERVAL '5 days',
  NOW() - INTERVAL '5 days'
),
(
  gen_random_uuid(),
  '00000000-0000-0000-0000-000000000001',
  'Arbeitsvertrag – Standard',
  E'# ARBEITSVERTRAG\n\nZwischen\n\n[Arbeitgeber]\n[Adresse]\n- Arbeitgeber -\n\nund\n\n[Arbeitnehmer]\n[Adresse]\n- Arbeitnehmer -\n\nwird folgender Arbeitsvertrag geschlossen:\n\n## § 1 Beginn und Art der Tätigkeit\n\nDer Arbeitnehmer wird ab dem [Datum] als [Position] eingestellt.\n\n## § 2 Arbeitszeit\n\nDie regelmäßige wöchentliche Arbeitszeit beträgt [40] Stunden.\n\n## § 3 Vergütung\n\nDas monatliche Bruttogehalt beträgt [Betrag] EUR.\n\n## § 4 Urlaub\n\nDer Arbeitnehmer hat Anspruch auf [30] Arbeitstage Urlaub pro Kalenderjahr.\n\n## § 5 Kündigungsfristen\n\nEs gelten die gesetzlichen Kündigungsfristen.',
  'Arbeitsrecht',
  NOW() - INTERVAL '25 days',
  NOW() - INTERVAL '25 days'
),
(
  gen_random_uuid(),
  '00000000-0000-0000-0000-000000000001',
  'Mietvertrag – Wohnraum',
  E'# MIETVERTRAG FÜR WOHNRAUM\n\nZwischen\n\n[Vermieter]\n[Adresse]\n- Vermieter -\n\nund\n\n[Mieter]\n[Adresse]\n- Mieter -\n\nwird folgender Mietvertrag geschlossen:\n\n## § 1 Mietobjekt\n\nVermietet wird die Wohnung im [Stockwerk] mit [Anzahl] Zimmern in [Adresse].\n\n## § 2 Mietzins\n\nDie monatliche Grundmiete beträgt [Betrag] EUR.\nDie monatlichen Nebenkosten betragen [Betrag] EUR.\n\n## § 3 Kaution\n\nDer Mieter leistet eine Kaution in Höhe von [3] Monatskaltmieten.\n\n## § 4 Mietbeginn\n\nDas Mietverhältnis beginnt am [Datum].\n\n## § 5 Kündigungsfrist\n\nDie gesetzliche Kündigungsfrist beträgt 3 Monate zum Monatsende.',
  'Mietrecht',
  NOW() - INTERVAL '8 days',
  NOW() - INTERVAL '8 days'
);
