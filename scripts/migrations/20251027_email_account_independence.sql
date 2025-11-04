-- Strengthen separation between portal login email and linked mailbox accounts
ALTER TABLE email_accounts
  ADD COLUMN IF NOT EXISTS login_email_snapshot TEXT;

ALTER TABLE email_accounts
  ADD COLUMN IF NOT EXISTS link_source TEXT;

WITH user_emails AS (
  SELECT id, LOWER(email) AS email FROM users
)
UPDATE email_accounts ea
SET
  link_source = CASE
    WHEN ea.link_source IS NULL OR ea.link_source NOT IN ('oauth', 'migration', 'manual', 'legacy', 'login') THEN
      CASE
        WHEN ue.email IS NOT NULL AND LOWER(ea.email_address) = ue.email THEN 'legacy'
        ELSE 'oauth'
      END
    ELSE ea.link_source
  END,
  login_email_snapshot = COALESCE(ea.login_email_snapshot, ue.email)
FROM user_emails ue
WHERE ea.user_id = ue.id;

ALTER TABLE email_accounts
  ALTER COLUMN link_source SET DEFAULT 'oauth';

UPDATE email_accounts
SET link_source = 'oauth'
WHERE link_source IS NULL;

ALTER TABLE email_accounts
  ALTER COLUMN link_source SET NOT NULL;

ALTER TABLE email_accounts
  DROP CONSTRAINT IF EXISTS email_accounts_link_source_check;

ALTER TABLE email_accounts
  ADD CONSTRAINT email_accounts_link_source_check
  CHECK (link_source IN ('oauth', 'migration', 'manual', 'legacy', 'login'));

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
