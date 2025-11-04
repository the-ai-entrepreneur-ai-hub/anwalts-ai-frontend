import asyncpg
import os
import uuid
import logging
import hashlib
import base64
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
import json
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

DEFAULT_ORG_SETTINGS: Dict[str, Any] = {
    "language": "de",
    "timezone": "Europe/Berlin",
    "require_two_factor": False,
    "enable_sso": False,
    "password_min_length": True,
    "password_require_special": True,
    "password_require_numbers": True,
    "email_notifications": True,
    "browser_notifications": False,
    "ai_updates": True,
    "ai_model": "qwen_legal_q4_k_m",
    "ai_creativity": 70,
    "auto_save": True,
}

class Database:
    def __init__(self):
        self.pool = None
        self.connection_string = self._get_connection_string()
        self._template_usage_ready = False
        self._service_health_ready = False
        self._email_cipher: Optional[Fernet] = None
        self._chat_schema_ready = False
        self._email_summary_schema_ready = False

    async def update_user_password(self, user_id: uuid.UUID, new_password_hash: str) -> bool:
        """Update password hash for a user (non-destructive)."""
        try:
            async with self.get_connection() as conn:
                await conn.execute(
                    "UPDATE users SET password_hash = $1 WHERE id = $2",
                    new_password_hash, user_id
                )
                return True
        except Exception as e:
            logger.error(f"Error updating password for user {user_id}: {e}")
            return False
    
    def _get_connection_string(self):
        """Build PostgreSQL connection string from environment variables"""
        host = os.getenv("POSTGRES_HOST", "postgres")
        port = os.getenv("POSTGRES_PORT", "5432")
        database = os.getenv("POSTGRES_DB", "anwalts_ai")
        user = os.getenv("POSTGRES_USER", "anwalts_user")
        password = os.getenv("POSTGRES_PASSWORD", "postgres")
        
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"

    def _build_email_cipher(self) -> Fernet:
        secret = (
            os.getenv("EMAIL_ACCOUNT_SECRET")
            or os.getenv("JWT_SECRET_KEY")
            or os.getenv("JWT_SECRET")
            or os.getenv("JWT_SECRET_KEY_FALLBACK")
        )
        if not secret:
            raise RuntimeError("EMAIL_ACCOUNT_SECRET or JWT_SECRET_KEY must be configured for email account encryption")
        if isinstance(secret, str):
            secret_bytes = secret.encode("utf-8")
        else:
            secret_bytes = secret
        key = base64.urlsafe_b64encode(secret_bytes[:32].ljust(32, b"0"))
        return Fernet(key)

    def _get_email_cipher(self) -> Fernet:
        if not self._email_cipher:
            try:
                self._email_cipher = self._build_email_cipher()
            except Exception as cipher_error:
                logger.error(f"Failed to initialise email account cipher: {cipher_error}")
                raise
        return self._email_cipher

    def _encrypt_refresh_token(self, token: str) -> str:
        try:
            cipher = self._get_email_cipher()
            return cipher.encrypt(token.encode("utf-8")).decode("utf-8")
        except Exception as enc_err:
            logger.error(f"Encrypt refresh token failed: {enc_err}")
            raise

    def _decrypt_refresh_token(self, encrypted: str) -> Optional[str]:
        if not encrypted:
            return None
        try:
            cipher = self._get_email_cipher()
            return cipher.decrypt(encrypted.encode("utf-8")).decode("utf-8")
        except Exception as dec_err:
            logger.error(f"Decrypt refresh token failed: {dec_err}")
            return None

    def _encrypt_secret(self, secret: str) -> str:
        """Encrypt arbitrary credential values using the email cipher."""
        if secret is None:
            raise ValueError("Secret value is required for encryption")
        return self._encrypt_refresh_token(secret)

    def _decrypt_secret(self, encrypted: str) -> Optional[str]:
        """Decrypt credential values stored with _encrypt_secret."""
        return self._decrypt_refresh_token(encrypted)

    def _serialize_email_account(self, row: asyncpg.Record) -> Dict[str, Any]:
        if not row:
            return {}
        return {
            "id": row["id"],
            "user_id": row["user_id"],
            "provider": row["provider"],
            "email_address": row["email_address"],
            "display_name": row.get("display_name"),
            "login_email_snapshot": row.get("login_email_snapshot"),
            "link_source": row.get("link_source"),
            "is_primary": row.get("is_primary", False),
            "oauth_consent": row.get("oauth_consent", False),
            "ai_read_consent": row.get("ai_read_consent", False),
            "draft_only_mode": row.get("draft_only_mode", True),
            "consent_timestamp": row.get("consent_timestamp"),
            "ai_consent_revoked_at": row.get("ai_consent_revoked_at"),
            "last_consent_update": row.get("last_consent_update"),
            "linked_at": row.get("linked_at"),
            "last_connected_at": row.get("last_connected_at"),
            "revoked_at": row.get("revoked_at"),
            "updated_at": row.get("updated_at"),
            "scopes": row.get("scopes") or [],
        }

    @staticmethod
    def _default_email_scopes() -> List[str]:
        return [
            "https://www.googleapis.com/auth/gmail.readonly",
            "https://www.googleapis.com/auth/gmail.modify",
        ]

    async def _maybe_migrate_profile_email_account(self, user_id: uuid.UUID) -> None:
        """One-time migration from legacy user_profiles Gmail storage to email_accounts."""
        try:
            async with self.get_connection() as conn:
                profile_row = await conn.fetchrow(
                    "SELECT data FROM user_profiles WHERE user_id = $1",
                    user_id,
                )
                if not profile_row or not profile_row["data"]:
                    return
                data = json.loads(profile_row["data"]) if isinstance(profile_row["data"], str) else dict(profile_row["data"])
                encrypted_token = data.get("gmail_refresh_token")
                if not encrypted_token:
                    return
                existing_account = await conn.fetchrow(
                    "SELECT 1 FROM email_accounts WHERE user_id = $1 LIMIT 1",
                    user_id,
                )
                if existing_account:
                    return

                refresh_token = self._decrypt_refresh_token(encrypted_token)
                if not refresh_token:
                    return

                user_row = await conn.fetchrow("SELECT email, name FROM users WHERE id = $1", user_id)
                if not user_row:
                    return

                gmail_email = (data.get("gmail_email") or "").strip().lower()
                user_login_email = (user_row["email"] or "").strip().lower()
                if not gmail_email:
                    logger.debug("Skipping legacy Gmail migration for %s: no gmail_email present", user_id)
                    return
                if gmail_email == user_login_email:
                    logger.debug(
                        "Skipping legacy Gmail migration for %s: gmail email matches login email %s",
                        user_id,
                        user_login_email,
                    )
                    return
                display_name = data.get("gmail_display_name") or user_row.get("name")
                scopes = data.get("gmail_scopes") or self._default_email_scopes()
                oauth_consent = bool(data.get("gmail_oauth_consent"))
                ai_consent = bool(data.get("gmail_ai_read_consent"))
                draft_only = data.get("gmail_draft_only_mode")
                consent_ts = data.get("gmail_consent_timestamp")
                if isinstance(consent_ts, str):
                    try:
                        consent_ts = datetime.fromisoformat(consent_ts)
                    except Exception:
                        consent_ts = None
                try:
                    await self.upsert_email_account(
                        user_id=user_id,
                        provider="google",
                        email_address=gmail_email,
                        display_name=display_name,
                        refresh_token=refresh_token,
                        scopes=scopes,
                        oauth_consent=oauth_consent,
                        ai_read_consent=ai_consent,
                        draft_only_mode=draft_only if draft_only is not None else True,
                        consent_timestamp=consent_ts,
                        last_connected_at=datetime.utcnow(),
                        link_source="migration",
                        login_email_snapshot=user_login_email,
                    )
                except ValueError as validation_err:
                    logger.warning(
                        "Migration-supplied Gmail account for %s skipped: %s",
                        user_id,
                        validation_err,
                    )
                    return

                # Clear legacy fields to prevent double usage
                for key in list(data.keys()):
                    if key.startswith("gmail_"):
                        data.pop(key)
                await conn.execute(
                    "UPDATE user_profiles SET data = $1, updated_at = NOW() WHERE user_id = $2",
                    json.dumps(data),
                    user_id,
                )
        except Exception as migrate_err:
            logger.warning(f"Gmail profile migration skipped for {user_id}: {migrate_err}")

    async def upsert_email_account(
        self,
        *,
        user_id: uuid.UUID,
        provider: str,
        email_address: str,
        display_name: Optional[str],
        refresh_token: str,
        scopes: Optional[List[str]] = None,
        oauth_consent: Optional[bool] = None,
        ai_read_consent: Optional[bool] = None,
        draft_only_mode: Optional[bool] = None,
        consent_timestamp: Optional[datetime] = None,
        last_connected_at: Optional[datetime] = None,
        login_email_snapshot: Optional[str] = None,
        link_source: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create or update an email account for the given user."""
        scopes = scopes or self._default_email_scopes()
        encrypted_token = self._encrypt_refresh_token(refresh_token)
        normalized_email = (email_address or "").strip().lower()
        normalized_snapshot = (login_email_snapshot or "").strip().lower() or None
        if not normalized_email:
            raise ValueError("Email address is required to link an email account.")

        allowed_sources = {"oauth", "migration", "manual", "legacy", "login"}
        requested_source = (link_source or "").strip().lower() or None
        if requested_source and requested_source not in allowed_sources:
            raise ValueError(f"Unsupported email account source '{requested_source}'.")

        now = datetime.utcnow()

        async with self.get_connection() as conn:
            user_row = await conn.fetchrow(
                "SELECT email FROM users WHERE id = $1",
                user_id,
            )
            login_email = (user_row["email"] or "").strip().lower() if user_row else ""
            existing = await conn.fetchrow(
                "SELECT * FROM email_accounts WHERE user_id = $1 AND email_address = $2",
                user_id,
                normalized_email,
            )

            existing_source = (existing.get("link_source") or "").strip().lower() if existing else None
            source = requested_source or existing_source or "oauth"
            if source not in allowed_sources:
                source = "oauth"

            # REMOVED RESTRICTION: Allow users to link their primary email (same as login)
            # Users commonly want to link their work email which is also their login email
            # No security issue since user is already authenticated
            # if normalized_email == login_email and source not in {"legacy", "login"}:
            #     raise ValueError("Verkn?pftes E-Mail-Konto darf nicht mit der Login-E-Mail identisch sein.")

            # CRITICAL FIX: Remove login_email_snapshot interference to make email accounts independent
            # Email accounts should NEVER interfere with authentication tokens
            snapshot_to_store = None  # Don't store snapshot at all
            if existing:
                # Remove any existing snapshot logic - email accounts are independent
                pass

            if existing:
                new_display_name = display_name or existing.get("display_name")
                new_scopes = scopes or (existing.get("scopes") or self._default_email_scopes())
                new_oauth_consent = existing.get("oauth_consent", False) if oauth_consent is None else oauth_consent
                new_ai_consent = existing.get("ai_read_consent", False) if ai_read_consent is None else ai_read_consent
                new_draft_only = existing.get("draft_only_mode", True) if draft_only_mode is None else bool(draft_only_mode)
                new_consent_ts = consent_timestamp or existing.get("consent_timestamp")
                consent_updated = False
                if oauth_consent is not None or ai_read_consent is not None or draft_only_mode is not None:
                    consent_updated = True
                    if new_oauth_consent and new_ai_consent and new_consent_ts is None:
                        new_consent_ts = now
                    if not (new_oauth_consent and new_ai_consent):
                        # If either consent revoked, clear timestamp
                        new_consent_ts = None
                await conn.execute(
                    """
                    UPDATE email_accounts
                    SET display_name = $1,
                        login_email_snapshot = $2,
                        link_source = $3,
                        refresh_token_encrypted = $4,
                        scopes = $5,
                        oauth_consent = $6,
                        ai_read_consent = $7,
                        draft_only_mode = $8,
                        consent_timestamp = $9,
                        last_consent_update = CASE WHEN $10 THEN $11 ELSE last_consent_update END,
                        last_connected_at = $12,
                        revoked_at = NULL,
                        updated_at = $11
                    WHERE id = $13
                    """,
                    new_display_name,
                    snapshot_to_store,
                    source,
                    encrypted_token,
                    new_scopes,
                    new_oauth_consent,
                    new_ai_consent,
                    new_draft_only,
                    new_consent_ts,
                    consent_updated,
                    now,
                    last_connected_at or now,
                    existing["id"],
                )
                account_row = await conn.fetchrow("SELECT * FROM email_accounts WHERE id = $1", existing["id"])
            else:
                # Determine if this should become primary
                existing_count = await conn.fetchval(
                    "SELECT COUNT(*) FROM email_accounts WHERE user_id = $1",
                    user_id,
                )
                is_primary = existing_count == 0
                account_id = uuid.uuid4()
                linked_at = last_connected_at or now
                consent_ts = consent_timestamp
                if consent_ts is None and oauth_consent and ai_read_consent:
                    consent_ts = now
                await conn.execute(
                    """
                    INSERT INTO email_accounts (
                        id, user_id, provider, email_address, display_name,
                        login_email_snapshot, link_source,
                        refresh_token_encrypted, scopes, is_primary,
                        oauth_consent, ai_read_consent, draft_only_mode,
                        consent_timestamp, ai_consent_revoked_at,
                        last_consent_update, linked_at, last_connected_at,
                        revoked_at, updated_at
                    )
                    VALUES (
                        $1, $2, $3, $4, $5,
                        $6, $7,
                        $8, $9, $10,
                        COALESCE($11, FALSE), COALESCE($12, FALSE), COALESCE($13, TRUE),
                        $14, NULL,
                        NOW(), $15, $16,
                        NULL, NOW()
                    )
                    """,
                    account_id,
                    user_id,
                    provider,
                    normalized_email,
                    display_name,
                    snapshot_to_store,
                    source,
                    encrypted_token,
                    scopes,
                    is_primary,
                    oauth_consent,
                    ai_read_consent,
                    draft_only_mode if draft_only_mode is not None else True,
                    consent_ts,
                    linked_at,
                    last_connected_at or now,
                )
                account_row = await conn.fetchrow("SELECT * FROM email_accounts WHERE id = $1", account_id)

            # Ensure active preference points to this account if none selected
            pref_row = await conn.fetchrow(
                "SELECT active_account_id FROM user_email_preferences WHERE user_id = $1",
                user_id,
            )
            active_id = pref_row["active_account_id"] if pref_row else None
            if not active_id:
                await conn.execute(
                    """
                    INSERT INTO user_email_preferences (user_id, active_account_id, updated_at)
                    VALUES ($1, $2, NOW())
                    ON CONFLICT (user_id) DO UPDATE
                    SET active_account_id = $2, updated_at = NOW()
                    """,
                    user_id,
                    account_row["id"],
                )
            return self._serialize_email_account(account_row)

    async def list_email_accounts(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        await self._maybe_migrate_profile_email_account(user_id)
        async with self.get_connection() as conn:
            rows = await conn.fetch(
                """
                SELECT *
                FROM email_accounts
                WHERE user_id = $1 AND revoked_at IS NULL
                ORDER BY linked_at ASC
                """,
                user_id,
            )
        accounts = [self._serialize_email_account(row) for row in rows]
        active = await self.get_active_email_account(user_id)
        active_id = active.get("id") if active else None
        for item in accounts:
            item["is_active"] = item["id"] == active_id
            item.pop("refresh_token_encrypted", None)
        return accounts

    async def get_email_account(self, user_id: uuid.UUID, account_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        await self._maybe_migrate_profile_email_account(user_id)
        async with self.get_connection() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM email_accounts WHERE id = $1 AND user_id = $2 AND revoked_at IS NULL",
                account_id,
                user_id,
            )
        if not row:
            return None
        return self._serialize_email_account(row)

    async def get_active_email_account(self, user_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        await self._maybe_migrate_profile_email_account(user_id)
        async with self.get_connection() as conn:
            row = await conn.fetchrow(
                """
                SELECT ea.*
                FROM user_email_preferences pref
                JOIN email_accounts ea ON pref.active_account_id = ea.id
                WHERE pref.user_id = $1 AND ea.revoked_at IS NULL
                """,
                user_id,
            )
        if not row:
            return None
        return self._serialize_email_account(row)

    async def set_active_email_account(self, user_id: uuid.UUID, account_id: uuid.UUID) -> bool:
        account = await self.get_email_account(user_id, account_id)
        if not account:
            return False
        async with self.get_connection() as conn:
            await conn.execute(
                """
                INSERT INTO user_email_preferences (user_id, active_account_id, updated_at)
                VALUES ($1, $2, NOW())
                ON CONFLICT (user_id)
                DO UPDATE SET active_account_id = EXCLUDED.active_account_id, updated_at = NOW()
                """,
                user_id,
                account_id,
            )
        return True

    async def clear_active_email_account(self, user_id: uuid.UUID) -> None:
        async with self.get_connection() as conn:
            await conn.execute(
                "DELETE FROM user_email_preferences WHERE user_id = $1",
                user_id,
            )

    async def create_domain_email_account(
        self,
        user_id: uuid.UUID,
        *,
        email_address: str,
        host: str,
        port: int,
        username: str,
        password: str,
        use_ssl: bool,
        protocol: str,
        mailbox_access_consent: bool,
        ai_read_consent: bool,
        status: Optional[str] = None,
        verified_at: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Store credentials for a firm domain email connector."""
        encrypted_secret = self._encrypt_secret(password)
        now = datetime.utcnow()
        status_value = status or "connected"
        verified_timestamp = verified_at or now
        account_id = uuid.uuid4()
        try:
            async with self.get_connection() as conn:
                await conn.execute(
                    """
                    INSERT INTO domain_email_accounts (
                        id, user_id, email_address, host, port, username, credential_encrypted,
                        use_ssl, protocol, mailbox_access_consent, ai_read_consent,
                        last_verified_at, last_status, created_at, updated_at
                    )
                    VALUES (
                        $1, $2, $3, $4, $5, $6, $7,
                        $8, $9, $10, $11,
                        $12, $13, $14, $15
                    )
                    """,
                    account_id,
                    user_id,
                    email_address.strip().lower(),
                    host.strip(),
                    int(port),
                    username.strip(),
                    encrypted_secret,
                    bool(use_ssl),
                    (protocol or "imap").strip().lower(),
                    bool(mailbox_access_consent),
                    bool(ai_read_consent),
                    verified_timestamp,
                    status_value,
                    now,
                    now,
                )
        except Exception as exc:
            logger.error(f"Error storing domain email connector for user {user_id}: {exc}")
            raise
        return await self.get_domain_email_account(account_id, user_id=user_id)

    async def get_domain_email_account(
        self,
        account_id: uuid.UUID,
        *,
        user_id: Optional[uuid.UUID] = None,
    ) -> Optional[Dict[str, Any]]:
        """Fetch a single domain email connector by id."""
        try:
            async with self.get_connection() as conn:
                if user_id:
                    row = await conn.fetchrow(
                        """
                        SELECT *
                        FROM domain_email_accounts
                        WHERE id = $1 AND user_id = $2
                        """,
                        account_id,
                        user_id,
                    )
                else:
                    row = await conn.fetchrow(
                        "SELECT * FROM domain_email_accounts WHERE id = $1",
                        account_id,
                    )
                if not row:
                    return None
                return {
                    "id": row["id"],
                    "user_id": row["user_id"],
                    "email_address": row["email_address"],
                    "host": row["host"],
                    "port": row["port"],
                    "username": row["username"],
                    "use_ssl": row["use_ssl"],
                    "protocol": row["protocol"],
                    "mailbox_access_consent": row["mailbox_access_consent"],
                    "ai_read_consent": row["ai_read_consent"],
                    "last_verified_at": row["last_verified_at"],
                    "last_status": row["last_status"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
        except Exception as exc:
            logger.error(f"Error fetching domain email connector {account_id}: {exc}")
            return None

    async def list_domain_email_accounts(self, user_id: uuid.UUID) -> List[Dict[str, Any]]:
        """List domain email connectors for a given admin user."""
        try:
            async with self.get_connection() as conn:
                rows = await conn.fetch(
                    """
                    SELECT *
                    FROM domain_email_accounts
                    WHERE user_id = $1
                    ORDER BY created_at DESC
                    """,
                    user_id,
                )
            results = []
            for row in rows:
                results.append({
                    "id": row["id"],
                    "user_id": row["user_id"],
                    "email_address": row["email_address"],
                    "host": row["host"],
                    "port": row["port"],
                    "username": row["username"],
                    "use_ssl": row["use_ssl"],
                    "protocol": row["protocol"],
                    "mailbox_access_consent": row["mailbox_access_consent"],
                    "ai_read_consent": row["ai_read_consent"],
                    "last_verified_at": row["last_verified_at"],
                    "last_status": row["last_status"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                })
            return results
        except Exception as exc:
            logger.error(f"Error listing domain email connectors for user {user_id}: {exc}")
            return []

    async def delete_domain_email_account(self, account_id: uuid.UUID, *, user_id: uuid.UUID) -> bool:
        """Delete a domain email connector."""
        try:
            async with self.get_connection() as conn:
                result = await conn.execute(
                    "DELETE FROM domain_email_accounts WHERE id = $1 AND user_id = $2",
                    account_id,
                    user_id,
                )
            return result.split()[-1] != "0"
        except Exception as exc:
            logger.error(f"Error deleting domain email connector {account_id}: {exc}")
            return False

    async def update_domain_email_account_status(
        self,
        account_id: uuid.UUID,
        *,
        user_id: uuid.UUID,
        status: str,
        verified_at: Optional[datetime] = None,
    ) -> bool:
        """Update last known status for a domain email connector."""
        try:
            async with self.get_connection() as conn:
                result = await conn.execute(
                    """
                    UPDATE domain_email_accounts
                    SET last_status = $1,
                        last_verified_at = COALESCE($2, last_verified_at),
                        updated_at = NOW()
                    WHERE id = $3 AND user_id = $4
                    """,
                    status,
                    verified_at,
                    account_id,
                    user_id,
                )
            return result.split()[-1] != "0"
        except Exception as exc:
            logger.error(f"Error updating domain email connector {account_id}: {exc}")
            return False
    async def get_email_account_refresh_token(
        self, user_id: uuid.UUID, account_id: Optional[uuid.UUID] = None
    ) -> Optional[str]:
        await self._maybe_migrate_profile_email_account(user_id)
        if account_id is None:
            active = await self.get_active_email_account(user_id)
            if not active:
                return None
            account_id = active["id"]
        async with self.get_connection() as conn:
            row = await conn.fetchrow(
                """
                SELECT refresh_token_encrypted
                FROM email_accounts
                WHERE id = $1 AND user_id = $2 AND revoked_at IS NULL
                """,
                account_id,
                user_id,
            )
        if not row:
            return None
        return self._decrypt_refresh_token(row["refresh_token_encrypted"])

    async def revoke_email_account(self, user_id: uuid.UUID, account_id: uuid.UUID) -> bool:
        async with self.get_connection() as conn:
            result = await conn.execute(
                """
                UPDATE email_accounts
                SET revoked_at = NOW(), updated_at = NOW()
                WHERE id = $1 AND user_id = $2
                """,
                account_id,
                user_id,
            )
            updated = result and result.endswith("1")
            if updated:
                await conn.execute(
                    "DELETE FROM user_email_preferences WHERE user_id = $1 AND active_account_id = $2",
                    user_id,
                    account_id,
                )
        return updated
    
    async def connect(self):
        """Initialize database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.connection_string,
                min_size=5,
                max_size=20,
                command_timeout=30,
                max_queries=50000,
                max_inactive_connection_lifetime=300
            )
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create database connection pool: {e}")
            raise
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")

    def get_connection(self):
        """Get a database connection from the pool"""
        if not self.pool:
            raise RuntimeError("Database not connected")
        return self.pool.acquire()

    async def ensure_settings_telemetry_schema(self):
        """Ensure supporting tables/columns for settings telemetry exist."""
        if self._service_health_ready:
            return
        try:
            async with self.get_connection() as conn:
                await conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS service_health_logs (
                        id UUID PRIMARY KEY,
                        service_name TEXT NOT NULL,
                        status BOOLEAN NOT NULL,
                        latency_ms INTEGER,
                        checked_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                    )
                    """
                )
                await conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_service_health_logs_service_checked
                    ON service_health_logs (service_name, checked_at DESC)
                    """
                )
                await conn.execute(
                    """
                    ALTER TABLE api_request_metrics
                    ADD COLUMN IF NOT EXISTS success_count INTEGER NOT NULL DEFAULT 0
                    """
                )
                await conn.execute(
                    """
                    ALTER TABLE api_request_metrics
                    ADD COLUMN IF NOT EXISTS error_count INTEGER NOT NULL DEFAULT 0
                    """
                )
                await conn.execute(
                    """
                    UPDATE api_request_metrics
                    SET success_count = request_count
                    WHERE success_count = 0 AND error_count = 0
                    """
                )
            self._service_health_ready = True
        except Exception as e:
            logger.error(f"Error ensuring settings telemetry schema: {e}")

    async def health_check(self):
        """Check database health"""
        try:
            async with self.get_connection() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            raise

    async def log_service_health(self, service_name: str, status: bool, latency_ms: Optional[int] = None):
        """Persist the outcome of a service health check."""
        await self.ensure_settings_telemetry_schema()
        try:
            async with self.get_connection() as conn:
                await conn.execute(
                    """
                    INSERT INTO service_health_logs (id, service_name, status, latency_ms, checked_at)
                    VALUES ($1, $2, $3, $4, NOW())
                    """,
                    uuid.uuid4(),
                    service_name,
                    status,
                    latency_ms
                )
                # Trim records older than 7 days to keep table compact
                await conn.execute(
                    "DELETE FROM service_health_logs WHERE checked_at < NOW() - INTERVAL '7 days'"
                )
        except Exception as e:
            logger.warning(f"Error logging health for {service_name}: {e}")

    async def get_service_health_summary(
        self, service_names: List[str], window_minutes: int = 1440
    ) -> Dict[str, Dict[str, Any]]:
        """Return uptime and latency aggregates for the requested services."""
        await self.ensure_settings_telemetry_schema()
        summary: Dict[str, Dict[str, Any]] = {
            name: {
                "uptime": None,
                "avg_latency_ms": None,
                "last_checked": None,
                "latest_status": None,
            }
            for name in service_names
        }
        if not service_names:
            return summary
        try:
            async with self.get_connection() as conn:
                aggregates = await conn.fetch(
                    """
                    SELECT
                        service_name,
                        COUNT(*) FILTER (WHERE status IS TRUE) AS success_count,
                        COUNT(*) AS total_count,
                        AVG(latency_ms) FILTER (WHERE latency_ms IS NOT NULL) AS avg_latency,
                        MAX(checked_at) AS last_checked
                    FROM service_health_logs
                    WHERE service_name = ANY($1::text[])
                      AND checked_at >= NOW() - ($2 || ' minutes')::interval
                    GROUP BY service_name
                    """,
                    service_names,
                    window_minutes,
                )
                latest = await conn.fetch(
                    """
                    SELECT DISTINCT ON (service_name)
                        service_name,
                        status,
                        latency_ms,
                        checked_at
                    FROM service_health_logs
                    WHERE service_name = ANY($1::text[])
                    ORDER BY service_name, checked_at DESC
                    """,
                    service_names,
                )
        except Exception as e:
            logger.warning(f"Error loading service health summary: {e}")
            return summary

        for row in aggregates:
            name = row["service_name"]
            total = int(row["total_count"] or 0)
            success = int(row["success_count"] or 0)
            uptime = None
            if total > 0:
                uptime = round((success / total) * 100, 2)
            summary[name]["uptime"] = uptime
            summary[name]["avg_latency_ms"] = (
                float(row["avg_latency"]) if row["avg_latency"] is not None else None
            )
            summary[name]["last_checked"] = row["last_checked"]

        for row in latest:
            name = row["service_name"]
            if name in summary:
                summary[name]["latest_status"] = bool(row["status"])
                summary[name]["last_checked"] = summary[name]["last_checked"] or row["checked_at"]
                if summary[name]["avg_latency_ms"] is None and row["latency_ms"] is not None:
                    summary[name]["avg_latency_ms"] = float(row["latency_ms"])

        return summary

    async def get_api_overview_metrics(self, window_days: int = 7) -> Dict[str, Any]:
        """Aggregate API traffic statistics for the given window."""
        try:
            async with self.get_connection() as conn:
                current = await conn.fetchrow(
                    """
                    SELECT
                        COALESCE(SUM(request_count), 0) AS total_calls,
                        COALESCE(SUM(total_latency_ms), 0) AS total_latency,
                        COALESCE(SUM(success_count), 0) AS success_calls,
                        COALESCE(SUM(error_count), 0) AS error_calls,
                        MAX(last_seen_at) AS last_seen
                    FROM api_request_metrics
                    WHERE bucket_start >= NOW() - ($1 || ' days')::interval
                    """,
                    window_days,
                )
                previous = await conn.fetchrow(
                    """
                    SELECT COALESCE(SUM(request_count), 0) AS total_calls
                    FROM api_request_metrics
                    WHERE bucket_start >= NOW() - ($1 || ' days')::interval
                      AND bucket_start < NOW() - ($2 || ' days')::interval
                    """,
                    window_days * 2,
                    window_days,
                )
        except Exception as e:
            logger.error(f"Error aggregating API overview metrics: {e}")
            return {
                "total_calls": 0,
                "total_latency": 0,
                "success_calls": 0,
                "error_calls": 0,
                "avg_latency_ms": 0.0,
                "previous_calls": 0,
                "last_seen": None,
            }

        total_calls = int(current["total_calls"] or 0)
        total_latency = int(current["total_latency"] or 0)
        success_calls = int(current["success_calls"] or 0)
        error_calls = int(current["error_calls"] or 0)
        avg_latency_ms = 0.0
        if total_calls > 0:
            avg_latency_ms = round(total_latency / total_calls, 2)

        return {
            "total_calls": total_calls,
            "total_latency": total_latency,
            "success_calls": success_calls,
            "error_calls": error_calls,
            "avg_latency_ms": avg_latency_ms,
            "previous_calls": int(previous["total_calls"] or 0) if previous else 0,
            "last_seen": current["last_seen"] if current else None,
        }
    
    # User management methods
    async def get_user_by_id(self, user_id: str):
        """Get user by ID"""
        try:
            async with self.get_connection() as conn:
                row = await conn.fetchrow(
                    """SELECT id, email, name, role, password_hash, created_at, is_active
                       FROM users
                       WHERE id = $1""",
                    uuid.UUID(user_id)
                )
                if row:
                    return UserInDB(**dict(row))
                return None
        except Exception as e:
            logger.error(f"Error getting user by ID {user_id}: {e}")
            return None
    
    async def get_user_by_email(self, email: str):
        """Get user by email"""
        try:
            async with self.get_connection() as conn:
                row = await conn.fetchrow(
                    """SELECT id, email, name, role, password_hash, created_at, is_active
                       FROM users
                       WHERE email = $1""",
                    email
                )
                if row:
                    return UserInDB(**dict(row))
                return None
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {e}")
            return None
    
    async def create_user(self, email: str, name: str, role: str, password_hash: str):
        """Create a new user"""
        try:
            async with self.get_connection() as conn:
                user_id = uuid.uuid4()
                await conn.execute(
                    """INSERT INTO users (id, email, name, role, password_hash, created_at, is_active) 
                       VALUES ($1, $2, $3, $4, $5, $6, $7)""",
                    user_id, email, name, role, password_hash, datetime.utcnow(), True
                )
                return await self.get_user_by_id(str(user_id))
        except Exception as e:
            logger.error(f"Error creating user {email}: {e}")
            raise

    async def list_recent_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Return most recently created users for dashboard summaries."""
        try:
            async with self.get_connection() as conn:
                rows = await conn.fetch(
                    """
                    SELECT id, email, name, role, created_at, is_active
                    FROM users
                    ORDER BY created_at DESC
                    LIMIT $1
                    """,
                    limit
                )
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error listing recent users: {e}")
            return []
    
    async def update_user_basic(self, user_id: uuid.UUID, name: str = None, role: str = None):
        """Update user basic information"""
        try:
            async with self.get_connection() as conn:
                if name and role:
                    await conn.execute(
                        "UPDATE users SET name = $1, role = $2 WHERE id = $3",
                        name, role, user_id
                    )
                elif name:
                    await conn.execute(
                        "UPDATE users SET name = $1 WHERE id = $2",
                        name, user_id
                    )
                elif role:
                    await conn.execute(
                        "UPDATE users SET role = $1 WHERE id = $2",
                        role, user_id
                    )
        except Exception as e:
            logger.error(f"Error updating user {user_id}: {e}")
            raise
    
    async def get_user_role(self, user_id: str) -> Optional[str]:
        """Get user role by ID"""
        try:
            async with self.get_connection() as conn:
                row = await conn.fetchrow(
                    "SELECT role FROM users WHERE id = $1",
                    uuid.UUID(user_id)
                )
                return row["role"] if row else None
        except Exception as e:
            logger.error(f"Error getting user role: {e}")
            return None

    async def set_user_as_admin(self, email: str) -> bool:
        """Promote user to admin role"""
        try:
            async with self.get_connection() as conn:
                result = await conn.execute(
                    "UPDATE users SET role = 'admin' WHERE LOWER(email) = LOWER($1)",
                    email
                )
                # Check if any rows were updated
                return result.split()[-1] != '0'
        except Exception as e:
            logger.error(f"Error setting user as admin: {e}")
            return False
    
    # User profile methods
    async def get_user_profile(self, user_id: uuid.UUID):
        """Get user profile"""
        try:
            async with self.get_connection() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM user_profiles WHERE user_id = $1",
                    user_id
                )
                if row:
                    return dict(row)
                return None
        except Exception as e:
            logger.error(f"Error getting user profile {user_id}: {e}")
            return None
    
    async def upsert_user_profile(self, user_id: uuid.UUID, profile_data):
        """Insert or update user profile"""
        try:
            async with self.get_connection() as conn:
                profile_dict = profile_data.model_dump() if hasattr(profile_data, 'model_dump') else dict(profile_data)
                
                # Remove None values
                profile_dict = {k: v for k, v in profile_dict.items() if v is not None}
                
                if profile_dict:
                    await conn.execute(
                        """INSERT INTO user_profiles (user_id, data, updated_at) 
                           VALUES ($1, $2, $3)
                           ON CONFLICT (user_id) 
                           DO UPDATE SET data = $2, updated_at = $3""",
                        user_id, json.dumps(profile_dict), datetime.utcnow()
                    )
                return profile_dict
        except Exception as e:
            logger.error(f"Error upserting user profile {user_id}: {e}")
            raise

    async def get_profile_picture(self, user_id: uuid.UUID) -> Optional[str]:
        """Get user profile picture base64 data"""
        try:
            async with self.get_connection() as conn:
                row = await conn.fetchrow(
                    "SELECT data FROM user_profiles WHERE user_id = $1",
                    user_id
                )
                if row and row['data']:
                    data = json.loads(row['data']) if isinstance(row['data'], str) else row['data']
                    return data.get('profile_picture')
                return None
        except Exception as e:
            logger.error(f"Error getting profile picture for user {user_id}: {e}")
            return None

    async def set_profile_picture(self, user_id: uuid.UUID, picture_data: str) -> bool:
        """Set or update user profile picture"""
        try:
            async with self.get_connection() as conn:
                # Get existing profile data
                row = await conn.fetchrow(
                    "SELECT data FROM user_profiles WHERE user_id = $1",
                    user_id
                )
                
                if row and row['data']:
                    data = json.loads(row['data']) if isinstance(row['data'], str) else row['data']
                else:
                    data = {}
                
                # Update profile picture
                data['profile_picture'] = picture_data
                data['profile_picture_uploaded_at'] = datetime.utcnow().isoformat()
                
                await conn.execute(
                    """INSERT INTO user_profiles (user_id, data, updated_at) 
                       VALUES ($1, $2, $3)
                       ON CONFLICT (user_id) 
                       DO UPDATE SET data = $2, updated_at = $3""",
                    user_id, json.dumps(data), datetime.utcnow()
                )
                return True
        except Exception as e:
            logger.error(f"Error setting profile picture for user {user_id}: {e}")
            return False

    async def delete_profile_picture(self, user_id: uuid.UUID) -> bool:
        """Remove user profile picture"""
        try:
            async with self.get_connection() as conn:
                # Get existing profile data
                row = await conn.fetchrow(
                    "SELECT data FROM user_profiles WHERE user_id = $1",
                    user_id
                )
                
                if row and row['data']:
                    data = json.loads(row['data']) if isinstance(row['data'], str) else row['data']
                    # Remove profile picture fields
                    data.pop('profile_picture', None)
                    data.pop('profile_picture_uploaded_at', None)
                    
                    await conn.execute(
                        "UPDATE user_profiles SET data = $1, updated_at = $2 WHERE user_id = $3",
                        json.dumps(data), datetime.utcnow(), user_id
                    )
                return True
        except Exception as e:
            logger.error(f"Error deleting profile picture for user {user_id}: {e}")
            return False

    async def set_gmail_refresh_token(
        self,
        user_id: uuid.UUID,
        refresh_token: str,
        *,
        email_address: str,
        display_name: Optional[str],
        scopes: Optional[List[str]] = None,
        oauth_consent: Optional[bool] = None,
        ai_read_consent: Optional[bool] = None,
        draft_only_mode: Optional[bool] = None,
        link_source: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Persist Gmail credentials using the email account model."""
        try:
            pending_consent = await self.get_pending_gmail_consent(user_id)
            pending_oauth = pending_consent.get("oauth_consent") if pending_consent else None
            pending_ai = pending_consent.get("ai_read_consent") if pending_consent else None
            pending_draft_only = pending_consent.get("draft_only_mode") if pending_consent else None

            effective_oauth = oauth_consent if oauth_consent is not None else pending_oauth
            effective_ai = ai_read_consent if ai_read_consent is not None else pending_ai
            effective_draft_only = draft_only_mode if draft_only_mode is not None else pending_draft_only

            if effective_oauth and effective_ai:
                if draft_only_mode is None or bool(draft_only_mode):
                    effective_draft_only = False
            elif effective_draft_only is None:
                effective_draft_only = True

            account = await self.upsert_email_account(
                user_id=user_id,
                provider="google",
                email_address=email_address,
                display_name=display_name,
                refresh_token=refresh_token,
                scopes=scopes,
                oauth_consent=effective_oauth,
                ai_read_consent=effective_ai,
                draft_only_mode=effective_draft_only,
                link_source=link_source or "oauth",
            )
            if account and pending_consent:
                await self.clear_pending_gmail_consent(user_id)
            return account
        except ValueError:
            raise
        except Exception as exc:
            logger.error(f"Error storing Gmail refresh token for user {user_id}: {exc}")
            return None

    async def get_gmail_refresh_token(
        self,
        user_id: uuid.UUID,
        account_id: Optional[uuid.UUID] = None,
    ) -> Optional[str]:
        """Retrieve the decrypted refresh token for the selected email account."""
        try:
            return await self.get_email_account_refresh_token(user_id, account_id)
        except Exception as exc:
            logger.error(f"Error retrieving Gmail refresh token for user {user_id}: {exc}")
            return None

    async def get_gmail_connection_status(self, user_id: uuid.UUID) -> dict:
        """Return connection status and available accounts for the user."""
        try:
            accounts = await self.list_email_accounts(user_id)
            active = await self.get_active_email_account(user_id)

            def _clone(value: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
                if value is None:
                    return None
                if isinstance(value, dict):
                    return dict(value)
                try:
                    return dict(value)
                except Exception:
                    return {"id": str(value)} if value is not None else None

            accounts_cloned = []
            for account in accounts or []:
                cloned = _clone(account)
                if cloned:
                    accounts_cloned.append(cloned)

            active_cloned = _clone(active)

            return {
                "connected": bool(active_cloned),
                "active_account": active_cloned,
                "accounts": accounts_cloned,
                "oauth_consent": bool(active_cloned.get("oauth_consent")) if active_cloned else False,
                "ai_read_consent": bool(active_cloned.get("ai_read_consent")) if active_cloned else False,
                "draft_only_mode": bool(active_cloned.get("draft_only_mode")) if active_cloned else True,
                "consent_timestamp": active_cloned.get("consent_timestamp") if active_cloned else None,
                "has_refresh_token": bool(active_cloned),
            }
        except Exception as exc:
            logger.error(f"Error getting Gmail connection status for user {user_id}: {exc}")
            return {
                "connected": False,
                "accounts": [],
                "oauth_consent": False,
                "ai_read_consent": False,
                "draft_only_mode": True,
                "consent_timestamp": None,
                "has_refresh_token": False,
            }

    async def set_gmail_consent(
        self,
        user_id: uuid.UUID,
        oauth_consent: bool,
        ai_read_consent: bool,
        draft_only_mode: Optional[bool] = None,
    ) -> bool:
        """Update consent flags on the active email account."""
        try:
            active = await self.get_active_email_account(user_id)
            if not active:
                return False
            refresh_token = await self.get_email_account_refresh_token(user_id, active["id"])
            if not refresh_token:
                return False
            resolved_draft_only = draft_only_mode if draft_only_mode is not None else active.get("draft_only_mode")
            if oauth_consent and ai_read_consent:
                if draft_only_mode is None or bool(draft_only_mode):
                    resolved_draft_only = False
            elif resolved_draft_only is None:
                resolved_draft_only = True

            await self.upsert_email_account(
                user_id=user_id,
                provider="google",
                email_address=active["email_address"],
                display_name=active.get("display_name"),
                refresh_token=refresh_token,
                scopes=active.get("scopes") or self._default_email_scopes(),
                oauth_consent=oauth_consent,
                ai_read_consent=ai_read_consent,
                draft_only_mode=resolved_draft_only,
                link_source=active.get("link_source"),
                login_email_snapshot=None,  # CRITICAL FIX: Never store login_email_snapshot
            )
            return True
        except Exception as exc:
            logger.error(f"Error updating Gmail consent for user {user_id}: {exc}")
            return False

    async def set_pending_gmail_consent(
        self,
        user_id: uuid.UUID,
        *,
        oauth_consent: bool,
        ai_read_consent: bool,
        draft_only_mode: Optional[bool] = None,
    ) -> None:
        payload = {
            "oauth_consent": bool(oauth_consent),
            "ai_read_consent": bool(ai_read_consent),
            "draft_only_mode": True if draft_only_mode is None else bool(draft_only_mode),
            "saved_at": datetime.utcnow().isoformat(),
        }
        async with self.get_connection() as conn:
            row = await conn.fetchrow(
                "SELECT data FROM user_profiles WHERE user_id = $1",
                user_id,
            )
            data: Dict[str, Any] = {}
            if row and row["data"]:
                raw_data = row["data"]
                data = json.loads(raw_data) if isinstance(raw_data, str) else dict(raw_data)
            data["gmail_pending_consent"] = payload
            await conn.execute(
                """
                INSERT INTO user_profiles (user_id, data, updated_at)
                VALUES ($1, $2, NOW())
                ON CONFLICT (user_id)
                DO UPDATE SET data = EXCLUDED.data, updated_at = NOW()
                """,
                user_id,
                json.dumps(data),
            )

    async def get_pending_gmail_consent(self, user_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        async with self.get_connection() as conn:
            row = await conn.fetchrow(
                "SELECT data FROM user_profiles WHERE user_id = $1",
                user_id,
            )
        if not row or not row["data"]:
            return None
        raw_data = row["data"]
        try:
            data = json.loads(raw_data) if isinstance(raw_data, str) else dict(raw_data)
        except Exception:
            return None
        consent = data.get("gmail_pending_consent")
        if isinstance(consent, dict):
            return consent
        return None

    async def clear_pending_gmail_consent(self, user_id: uuid.UUID) -> None:
        async with self.get_connection() as conn:
            row = await conn.fetchrow(
                "SELECT data FROM user_profiles WHERE user_id = $1",
                user_id,
            )
            if not row or not row["data"]:
                return
            raw_data = row["data"]
            try:
                data = json.loads(raw_data) if isinstance(raw_data, str) else dict(raw_data)
            except Exception:
                return
            if "gmail_pending_consent" not in data:
                return
            data.pop("gmail_pending_consent", None)
            await conn.execute(
                """
                UPDATE user_profiles
                SET data = $1, updated_at = NOW()
                WHERE user_id = $2
                """,
                json.dumps(data),
                user_id,
            )

    async def revoke_gmail_access(self, user_id: uuid.UUID, account_id: Optional[uuid.UUID] = None) -> bool:
        """Revoke a linked Gmail account and remove active selection."""
        try:
            target_account = account_id
            if not target_account:
                active = await self.get_active_email_account(user_id)
                target_account = active["id"] if active else None
            if not target_account:
                return False
            return await self.revoke_email_account(user_id, uuid.UUID(str(target_account)))
        except Exception as exc:
            logger.error(f"Error revoking Gmail access for user {user_id}: {exc}")
            return False

    async def get_dashboard_summary(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """Aggregate key dashboard metrics for the given user."""
        try:
            async with self.get_connection() as conn:
                documents_row = await conn.fetchrow(
                    """
                    SELECT
                        COUNT(*) AS total_count,
                        COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') AS recent_count
                    FROM documents
                    WHERE user_id = $1
                    """,
                    user_id
                )

                messages_row = await conn.fetchrow(
                    """
                    SELECT
                        COUNT(*) AS total_count,
                        COUNT(*) FILTER (WHERE created_at >= NOW() - INTERVAL '30 days') AS recent_count
                    FROM assistant_messages
                    WHERE user_id = $1
                    """,
                    user_id
                )

                analytics_row = await conn.fetchval(
                    """
                    SELECT COUNT(*)
                    FROM analytics_events
                    WHERE user_id = $1
                      AND created_at >= NOW() - INTERVAL '30 days'
                      AND (event_type ILIKE 'case%' OR event_type ILIKE 'matter%' OR event_type ILIKE 'mandat%')
                    """,
                    user_id
                )

                next_deadline = await conn.fetchval(
                    """
                    SELECT expires_at
                    FROM api_tokens
                    WHERE user_id = $1
                      AND revoked_at IS NULL
                      AND expires_at IS NOT NULL
                      AND expires_at > NOW()
                    ORDER BY expires_at ASC
                    LIMIT 1
                    """,
                    user_id
                )

                documents_total = int(documents_row['total_count']) if documents_row and documents_row['total_count'] is not None else 0
                documents_recent = int(documents_row['recent_count']) if documents_row and documents_row['recent_count'] is not None else 0

                emails_total = int(messages_row['total_count']) if messages_row and messages_row['total_count'] is not None else 0
                emails_recent = int(messages_row['recent_count']) if messages_row and messages_row['recent_count'] is not None else 0

                new_cases = int(analytics_row) if analytics_row is not None else 0
                if new_cases == 0:
                    new_cases = documents_recent

                return {
                    "new_cases": new_cases,
                    "documents_total": documents_total,
                    "documents_recent": documents_recent,
                    "emails_total": emails_total,
                    "emails_recent": emails_recent,
                    "next_deadline": next_deadline.isoformat() if next_deadline else None,
                    "generated_at": datetime.utcnow().isoformat() + 'Z'
                }
        except Exception as e:
            logger.error(f"Error aggregating dashboard summary for user {user_id}: {e}")
            raise

    # Settings admin helpers
    async def get_org_settings(self) -> Dict[str, Any]:
        """Fetch persisted organization-wide settings."""
        try:
            async with self.get_connection() as conn:
                row = await conn.fetchrow(
                    """SELECT language, timezone, require_two_factor, enable_sso,
                              password_min_length, password_require_special,
                              password_require_numbers, email_notifications,
                              browser_notifications, ai_updates, ai_model,
                              ai_creativity, auto_save
                       FROM organization_settings
                       ORDER BY updated_at DESC
                       LIMIT 1"""
                )
                if not row:
                    return dict(DEFAULT_ORG_SETTINGS)
                stored = dict(row)
                merged = dict(DEFAULT_ORG_SETTINGS)
                merged.update({k: stored.get(k, DEFAULT_ORG_SETTINGS[k]) for k in DEFAULT_ORG_SETTINGS})
                return merged
        except Exception as e:
            logger.error(f"Error loading organization settings: {e}")
            return dict(DEFAULT_ORG_SETTINGS)

    async def upsert_org_settings(self, settings: Dict[str, Any], updated_by: Optional[uuid.UUID] = None) -> Dict[str, Any]:
        """Persist organization settings."""
        payload = dict(DEFAULT_ORG_SETTINGS)
        payload.update({k: settings[k] for k in settings if k in DEFAULT_ORG_SETTINGS})
        try:
            async with self.get_connection() as conn:
                row = await conn.fetchrow("SELECT id FROM organization_settings LIMIT 1")
                if row:
                    await conn.execute(
                        """UPDATE organization_settings
                           SET language = $1,
                               timezone = $2,
                               require_two_factor = $3,
                               enable_sso = $4,
                               password_min_length = $5,
                               password_require_special = $6,
                               password_require_numbers = $7,
                               email_notifications = $8,
                               browser_notifications = $9,
                               ai_updates = $10,
                               ai_model = $11,
                               ai_creativity = $12,
                               auto_save = $13,
                               updated_at = NOW(),
                               updated_by = $14
                           WHERE id = $15""",
                        payload["language"],
                        payload["timezone"],
                        payload["require_two_factor"],
                        payload["enable_sso"],
                        payload["password_min_length"],
                        payload["password_require_special"],
                        payload["password_require_numbers"],
                        payload["email_notifications"],
                        payload["browser_notifications"],
                        payload["ai_updates"],
                        payload["ai_model"],
                        payload["ai_creativity"],
                        payload["auto_save"],
                        updated_by,
                        row["id"],
                    )
                else:
                    await conn.execute(
                        """INSERT INTO organization_settings (
                               language, timezone, require_two_factor, enable_sso,
                               password_min_length, password_require_special,
                               password_require_numbers, email_notifications,
                               browser_notifications, ai_updates, ai_model,
                               ai_creativity, auto_save, updated_by
                           ) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14)""",
                        payload["language"],
                        payload["timezone"],
                        payload["require_two_factor"],
                        payload["enable_sso"],
                        payload["password_min_length"],
                        payload["password_require_special"],
                        payload["password_require_numbers"],
                        payload["email_notifications"],
                        payload["browser_notifications"],
                        payload["ai_updates"],
                        payload["ai_model"],
                        payload["ai_creativity"],
                        payload["auto_save"],
                        updated_by,
                    )
            return payload
        except Exception as e:
            logger.error(f"Error saving organization settings: {e}")
            raise

    async def record_api_metric(self, method: str, path: str, status: int, latency_ms: int):
        """Aggregate API request metrics in per-minute buckets."""
        bucket_start = datetime.utcnow().replace(second=0, microsecond=0)
        success_increment = 1 if status < 500 else 0
        error_increment = 0 if success_increment == 1 else 1
        try:
            async with self.get_connection() as conn:
                await conn.execute(
                    """INSERT INTO api_request_metrics (bucket_start, method, path, request_count, total_latency_ms, max_latency_ms, last_status, last_seen_at, success_count, error_count)
                       VALUES ($1, $2, $3, 1, $4, $5, $6, NOW(), $7, $8)
                       ON CONFLICT (bucket_start, method, path)
                       DO UPDATE SET
                           request_count = api_request_metrics.request_count + 1,
                           total_latency_ms = api_request_metrics.total_latency_ms + EXCLUDED.total_latency_ms,
                           max_latency_ms = GREATEST(api_request_metrics.max_latency_ms, EXCLUDED.max_latency_ms),
                           last_status = EXCLUDED.last_status,
                           last_seen_at = NOW(),
                           success_count = api_request_metrics.success_count + EXCLUDED.success_count,
                           error_count = api_request_metrics.error_count + EXCLUDED.error_count""",
                    bucket_start,
                    method,
                    path,
                    latency_ms,
                    latency_ms,
                    status,
                    success_increment,
                    error_increment,
                )
        except Exception as e:
            logger.warning(f"Failed to record API metric for {method} {path}: {e}")

    async def get_api_endpoint_metrics(self, window_days: int = 7) -> List[Dict[str, Any]]:
        """Return aggregated API metrics for the given window."""
        try:
            async with self.get_connection() as conn:
                rows = await conn.fetch(
                    """SELECT method,
                              path,
                              SUM(request_count) AS total_calls,
                              SUM(success_count) AS success_calls,
                              SUM(error_count) AS error_calls,
                              SUM(total_latency_ms) AS total_latency,
                              MAX(request_count) AS peak_per_minute,
                              MAX(last_status) FILTER (WHERE last_status >= 500) AS last_error_status
                       FROM api_request_metrics
                       WHERE bucket_start >= NOW() - ($1 || ' days')::interval
                       GROUP BY method, path
                       ORDER BY total_calls DESC NULLS LAST""",
                    window_days
                )
                metrics: List[Dict[str, Any]] = []
                for row in rows:
                    call_count = int(row["total_calls"]) if row["total_calls"] else 0
                    total_latency_ms = int(row["total_latency"]) if row["total_latency"] else 0
                    avg_latency = 0
                    if call_count > 0:
                        avg_latency = round(total_latency_ms / call_count, 2)
                    success_calls = int(row["success_calls"]) if row["success_calls"] else 0
                    error_calls = int(row["error_calls"]) if row["error_calls"] else 0
                    success_rate = 0.0
                    if call_count > 0:
                        success_rate = round((success_calls / call_count) * 100, 2)
                    metrics.append(
                        {
                            "method": row["method"],
                            "path": row["path"],
                            "call_count": call_count,
                            "avg_latency_ms": avg_latency,
                            "peak_per_minute": int(row["peak_per_minute"] or 0),
                            "last_error_status": row["last_error_status"],
                            "success_calls": success_calls,
                            "error_calls": error_calls,
                            "success_rate": success_rate,
                        }
                    )
                return metrics
        except Exception as e:
            logger.error(f"Error aggregating API endpoint metrics: {e}")
            return []

    async def list_webhooks(self) -> List[Dict[str, Any]]:
        """Return all configured webhooks."""
        try:
            async with self.get_connection() as conn:
                rows = await conn.fetch(
                    """SELECT id, name, url, events, is_active, created_at, updated_at, secret
                       FROM webhooks
                       ORDER BY created_at DESC"""
                )
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error listing webhooks: {e}")
            return []

    async def get_webhook(self, webhook_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """Fetch single webhook."""
        try:
            async with self.get_connection() as conn:
                row = await conn.fetchrow(
                    """SELECT id, name, url, events, is_active, created_at, updated_at, secret
                       FROM webhooks WHERE id = $1""",
                    webhook_id,
                )
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error fetching webhook {webhook_id}: {e}")
            return None

    async def create_webhook(
        self,
        name: str,
        url: str,
        events: List[str],
        is_active: bool,
        secret: Optional[str],
        created_by: Optional[uuid.UUID],
    ) -> Dict[str, Any]:
        """Create webhook entry."""
        webhook_id = uuid.uuid4()
        now = datetime.utcnow()
        try:
            async with self.get_connection() as conn:
                await conn.execute(
                    """INSERT INTO webhooks (id, name, url, events, is_active, secret, created_at, updated_at, created_by)
                       VALUES ($1,$2,$3,$4,$5,$6,$7,$7,$8)""",
                    webhook_id, name, url, events, is_active, secret, now, created_by
                )
            return {
                "id": str(webhook_id),
                "name": name,
                "url": url,
                "events": events,
                "is_active": is_active,
                "secret": secret,
                "created_at": now,
                "updated_at": now,
            }
        except Exception as e:
            logger.error(f"Error creating webhook: {e}")
            raise

    async def update_webhook(
        self,
        webhook_id: uuid.UUID,
        name: str,
        url: str,
        events: List[str],
        is_active: bool,
        secret: Optional[str] = None,
    ) -> bool:
        """Update webhook."""
        try:
            async with self.get_connection() as conn:
                result = await conn.execute(
                    """UPDATE webhooks
                       SET name = $1,
                           url = $2,
                           events = $3,
                           is_active = $4,
                           secret = $5,
                           updated_at = $6
                       WHERE id = $7""",
                    name, url, events, is_active, secret, datetime.utcnow(), webhook_id
                )
                return result == "UPDATE 1"
        except Exception as e:
            logger.error(f"Error updating webhook {webhook_id}: {e}")
            raise

    async def delete_webhook(self, webhook_id: uuid.UUID) -> bool:
        """Delete webhook."""
        try:
            async with self.get_connection() as conn:
                result = await conn.execute("DELETE FROM webhooks WHERE id = $1", webhook_id)
                return result == "DELETE 1"
        except Exception as e:
            logger.error(f"Error deleting webhook {webhook_id}: {e}")
            raise

    async def record_webhook_log(
        self,
        webhook_id: uuid.UUID,
        status_code: Optional[int],
        latency_ms: Optional[int],
        response_body: Optional[str],
        trace_id: Optional[str] = None,
    ):
        """Store webhook delivery log entry."""
        try:
            async with self.get_connection() as conn:
                await conn.execute(
                    """INSERT INTO webhook_logs (id, webhook_id, status_code, latency_ms, response_body, created_at, trace_id)
                       VALUES ($1,$2,$3,$4,$5,$6,$7)""",
                    uuid.uuid4(), webhook_id, status_code, latency_ms, response_body, datetime.utcnow(), trace_id
                )
        except Exception as e:
            logger.error(f"Error recording webhook log for {webhook_id}: {e}")

    async def list_webhook_logs(self, webhook_id: uuid.UUID, limit: int = 10) -> List[Dict[str, Any]]:
        """Return recent webhook logs."""
        try:
            async with self.get_connection() as conn:
                rows = await conn.fetch(
                    """SELECT id, status_code, latency_ms, response_body, created_at, trace_id
                       FROM webhook_logs
                       WHERE webhook_id = $1
                       ORDER BY created_at DESC
                       LIMIT $2""",
                    webhook_id, limit
                )
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error loading webhook logs for {webhook_id}: {e}")
            return []

    async def list_users_paginated(
        self,
        search: Optional[str] = None,
        role: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Return users with optional filtering."""
        clauses = ["1=1"]
        params: List[Any] = []
        if search:
            params.extend([f"%{search.lower()}%", f"%{search.lower()}%"])
            first_idx = len(params) - 1
            second_idx = len(params)
            clauses.append(f"(LOWER(u.name) LIKE ${first_idx} OR LOWER(u.email) LIKE ${second_idx})")
        if role and role != "all":
            params.append(role)
            clauses.append(f"u.role = ${len(params)}")

        where_sql = " AND ".join(clauses)

        try:
            async with self.get_connection() as conn:
                total_row = await conn.fetchval(
                    f"SELECT COUNT(*) FROM users u WHERE {where_sql}",
                    *params
                )
                params_with_window = params + [limit, offset]
                limit_idx = len(params) + 1
                offset_idx = len(params) + 2
                rows = await conn.fetch(
                    f"""SELECT u.id, u.email, u.name, u.role, u.created_at, u.is_active,
                               COALESCE(msg.last_activity, u.created_at) AS last_activity
                        FROM users u
                        LEFT JOIN (
                            SELECT user_id, MAX(created_at) AS last_activity
                            FROM assistant_messages
                            GROUP BY user_id
                        ) msg ON msg.user_id = u.id
                        WHERE {where_sql}
                        ORDER BY u.created_at DESC
                        LIMIT ${limit_idx} OFFSET ${offset_idx}""",
                    *params_with_window,
                )
                return [dict(row) for row in rows], int(total_row or 0)
        except Exception as e:
            logger.error(f"Error listing users with filters: {e}")
            return [], 0

    async def set_user_active_state(self, user_id: uuid.UUID, active: bool) -> bool:
        """Activate or deactivate user."""
        try:
            async with self.get_connection() as conn:
                result = await conn.execute(
                    "UPDATE users SET is_active = $1 WHERE id = $2",
                    active, user_id
                )
                return result == "UPDATE 1"
        except Exception as e:
            logger.error(f"Error updating is_active for user {user_id}: {e}")
            return False

    async def change_user_role(self, user_id: uuid.UUID, role: str) -> bool:
        """Change role for user."""
        try:
            async with self.get_connection() as conn:
                result = await conn.execute(
                    "UPDATE users SET role = $1 WHERE id = $2",
                    role, user_id
                )
                return result == "UPDATE 1"
        except Exception as e:
            logger.error(f"Error changing role for user {user_id}: {e}")
            return False

    async def export_snapshot(self) -> Dict[str, Any]:
        """Collect snapshot data for exports."""
        snapshot: Dict[str, Any] = {}
        try:
            async with self.get_connection() as conn:
                users = await conn.fetch(
                    "SELECT id, email, name, role, created_at, is_active FROM users ORDER BY created_at DESC"
                )
                documents = await conn.fetch(
                    "SELECT id, user_id, title, created_at FROM documents ORDER BY created_at DESC"
                )
                templates = await conn.fetch(
                    "SELECT id, user_id, title, category, created_at FROM templates ORDER BY created_at DESC"
                )
                webhooks = await conn.fetch(
                    "SELECT id, name, url, events, is_active, created_at FROM webhooks ORDER BY created_at DESC"
                )

                snapshot["users"] = [dict(row) for row in users]
                snapshot["documents"] = [dict(row) for row in documents]
                snapshot["templates"] = [dict(row) for row in templates]
                snapshot["webhooks"] = [dict(row) for row in webhooks]
                return snapshot
        except Exception as e:
            logger.error(f"Error creating export snapshot: {e}")
            raise

    # Template methods
    async def get_templates(self, user_id: uuid.UUID, category: str = None):
        """Get templates for user"""
        try:
            async with self.get_connection() as conn:
                base_query = "SELECT id, title, content, category, created_at, updated_at FROM templates WHERE user_id = $1"
                params: list[Any] = [user_id]
                if category:
                    base_query += " AND category = $2"
                    params.append(category)
                base_query += " ORDER BY created_at DESC"
                rows = await conn.fetch(base_query, *params)
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting templates for user {user_id}: {e}")
            return []

    async def seed_default_templates(self, user_id: uuid.UUID) -> int:
        """Seed a curated set of German-law templates for a user if none exist.

        Returns number of templates inserted.
        """
        try:
            async with self.get_connection() as conn:
                # Only seed when the user has no templates at all
                existing = await conn.fetchval(
                    "SELECT COUNT(*) FROM templates WHERE user_id = $1",
                    user_id,
                )
                if existing and int(existing) > 0:
                    return 0

                now = datetime.utcnow()
                data = [
                    ("Geheimhaltungsvereinbarung (NDA) – Standard",
                     "<h2>Geheimhaltungsvereinbarung (NDA)</h2><p>Zwischen [Partei A] und [Partei B] wird folgende Vertraulichkeitsvereinbarung geschlossen. Schutz vertraulicher Informationen, Zweckbindung, Laufzeit, Vertragsstrafe, Gerichtsstand. Bezug: §§ 241, 280 BGB.</p>",
                     "Vertragsrecht"),
                    ("Mietvertrag – Wohnraum",
                     "<h2>Mietvertrag (Wohnraum)</h2><p>Vermieter: [Name], Mieter: [Name]. Mietsache: [Adresse/Objekt]. Mietbeginn, Miethöhe, Nebenkosten, Kaution, Instandhaltung, Kündigungsfristen. Bezug: §§ 535 ff. BGB.</p>",
                     "Zivilrecht"),
                    ("Arbeitsvertrag",
                     "<h2>Arbeitsvertrag</h2><p>Arbeitgeber [Firma] und Arbeitnehmer [Name] schließen folgenden Arbeitsvertrag. Tätigkeit, Arbeitszeit, Vergütung, Urlaub, Probezeit, Nebentätigkeit, Vertraulichkeit. Bezug: § 611a BGB, Nachweisgesetz.</p>",
                     "Arbeitsrecht"),
                    ("Kündigungsschutzklage",
                     "<h2>Kündigungsschutzklage</h2><p>Kläger [AN] gegen Beklagte [AG]. Antrag: Feststellung, dass die Kündigung vom [Datum] unwirksam ist. Sachverhalt, soziale Gesichtspunkte, Betriebsgröße, Fristwahrung gem. § 4 KSchG. Bezug: KSchG, ZPO.</p>",
                     "Arbeitsrecht"),
                    ("Auskunftsersuchen nach Art. 15 DSGVO",
                     "<h2>Auskunftsersuchen</h2><p>Sehr geehrte Damen und Herren, hiermit mache ich mein Recht auf Auskunft nach Art. 15 DSGVO geltend (Verarbeitungszwecke, Kategorien, Empfänger, Speicherdauer) und bitte um Kopie der personenbezogenen Daten. Bezug: Art. 12, 15 DSGVO.</p>",
                     "Datenschutz"),
                    ("Abmahnung – UWG",
                     "<h2>Abmahnung</h2><p>Sehr geehrte Damen und Herren, wegen des Wettbewerbsverstoßes [Beschreibung] fordern wir die Abgabe einer strafbewehrten Unterlassungserklärung bis [Datum]. Kostenerstattungsvorbehalt. Bezug: §§ 3, 8, 12 UWG.</p>",
                     "Wettbewerbsrecht"),
                    ("Allgemeine Geschäftsbedingungen (AGB) – Onlineshop",
                     "<h2>AGB</h2><p>Geltungsbereich, Begriffsbestimmungen, Vertragsschluss, Preise/Versand, Zahlungsarten, Widerruf, Gewährleistung, Haftung, Datenschutz, Schlussbestimmungen. Bezug: §§ 305 ff. BGB, §§ 312g, 355 BGB.</p>",
                     "Verbraucherrecht"),
                    ("Widerrufsbelehrung – Verbraucher",
                     "<h2>Widerrufsbelehrung</h2><p>Sie haben das Recht, binnen vierzehn Tagen ohne Angabe von Gründen diesen Vertrag zu widerrufen. Fristbeginn, Ausübung des Widerrufs, Folgen des Widerrufs. Bezug: § 312g, § 355 BGB.</p>",
                     "Verbraucherrecht"),
                    ("Gesellschaftsvertrag – GmbH",
                     "<h2>Gesellschaftsvertrag GmbH</h2><p>Firma und Sitz, Unternehmensgegenstand, Stammkapital, Geschäftsanteile, Geschäftsführung, Vertretung, Gesellschafterversammlung, Gewinnverwendung. Bezug: GmbHG.</p>",
                     "Gesellschaftsrecht"),
                    ("Widerspruch gegen Mahnbescheid",
                     "<h2>Widerspruch gegen Mahnbescheid</h2><p>Gegen den Mahnbescheid vom [Datum], Az. [xx], lege ich Widerspruch ein (voll/teilweise). Begründung erfolgt gesondert. Bezug: §§ 688 ff. ZPO.</p>",
                     "Zivilprozess"),
                ]

                inserted = 0
                for title, content, category in data:
                    template_id = uuid.uuid4()
                    await conn.execute(
                        """
                        INSERT INTO templates (id, user_id, title, content, category, created_at, updated_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $6)
                        """,
                        template_id, user_id, title, content, category, now
                    )
                    inserted += 1
                return inserted
        except Exception as e:
            logger.error(f"Error seeding default templates for user {user_id}: {e}")
            return 0

    async def get_template_by_id(self, template_id: uuid.UUID, user_id: uuid.UUID):
        """Fetch a single template for a user"""
        try:
            async with self.get_connection() as conn:
                row = await conn.fetchrow(
                    "SELECT id, title, content, category, created_at, updated_at FROM templates WHERE id = $1 AND user_id = $2",
                    template_id,
                    user_id
                )
                return dict(row) if row else None
        except Exception as e:
            logger.error(f"Error getting template {template_id} for user {user_id}: {e}")
            return None

    async def create_template(self, user_id: uuid.UUID, title: str, content: str, category: str = None):
        """Create a new template"""
        try:
            async with self.get_connection() as conn:
                template_id = uuid.uuid4()
                now = datetime.utcnow()
                row = await conn.fetchrow(
                    """INSERT INTO templates (id, user_id, title, content, category, created_at, updated_at)
                       VALUES ($1, $2, $3, $4, $5, $6, $7)
                       RETURNING id, title, content, category, created_at, updated_at""",
                    template_id, user_id, title, content, category, now, now
                )
                if not row:
                    return {
                        "id": str(template_id),
                        "title": title,
                        "content": content,
                        "category": category,
                        "created_at": now,
                        "updated_at": now,
                    }
                data = dict(row)
                data["id"] = str(data.get("id") or template_id)
                return data
        except Exception as e:
            logger.error(f"Error creating template for user {user_id}: {e}")
            raise

    async def update_template(
        self,
        template_id: uuid.UUID,
        user_id: uuid.UUID,
        title: str = None,
        content: str = None,
        category: str = None,
        expected_updated_at: datetime = None
    ):
        """Update a template"""
        try:
            async with self.get_connection() as conn:
                updates = []
                params: list[Any] = []
                param_count = 1

                if title is not None:
                    updates.append(f"title = ${param_count}")
                    params.append(title)
                    param_count += 1

                if content is not None:
                    updates.append(f"content = ${param_count}")
                    params.append(content)
                    param_count += 1

                if category is not None:
                    updates.append(f"category = ${param_count}")
                    params.append(category)
                    param_count += 1

                if not updates:
                    row = await conn.fetchrow(
                        "SELECT id, title, content, category, created_at, updated_at FROM templates WHERE id = $1 AND user_id = $2",
                        template_id,
                        user_id,
                    )
                    return dict(row) if row else None

                updates.append(f"updated_at = ${param_count}")
                new_updated_at = datetime.utcnow()
                params.append(new_updated_at)
                param_count += 1

                params.extend([template_id, user_id])

                where_parts = [f"id = ${param_count}", f"user_id = ${param_count + 1}"]
                if expected_updated_at:
                    where_parts.append(f"updated_at = ${param_count + 2}")
                    params.append(expected_updated_at)

                query = (
                    f"UPDATE templates SET {', '.join(updates)} "
                    f"WHERE {' AND '.join(where_parts)} "
                    "RETURNING id, title, content, category, created_at, updated_at"
                )
                row = await conn.fetchrow(query, *params)
                if row:
                    data = dict(row)
                    data["updated_at"] = data.get("updated_at") or new_updated_at
                    return data
                return None
        except Exception as e:
            logger.error(f"Error updating template {template_id}: {e}")
            raise

    async def delete_template(self, template_id: uuid.UUID, user_id: uuid.UUID, expected_updated_at: datetime = None):
        """Delete a template"""
        try:
            async with self.get_connection() as conn:
                params: list[Any] = [template_id, user_id]
                condition = "id = $1 AND user_id = $2"
                if expected_updated_at:
                    condition += " AND updated_at = $3"
                    params.append(expected_updated_at)

                result = await conn.execute(
                    f"DELETE FROM templates WHERE {condition}",
                    *params
                )
                if result == "DELETE 1":
                    await self._cleanup_template_usage(template_id, user_id)
                return result == "DELETE 1"
        except Exception as e:
            logger.error(f"Error deleting template {template_id}: {e}")
            return False

    async def _ensure_template_usage_table(self):
        if self._template_usage_ready:
            return
        try:
            async with self.get_connection() as conn:
                await conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS template_usage (
                        template_id UUID NOT NULL,
                        user_id UUID NOT NULL,
                        usage_count BIGINT NOT NULL DEFAULT 0,
                        last_used_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                        PRIMARY KEY (template_id, user_id)
                    )
                    """
                )
            self._template_usage_ready = True
        except Exception as e:
            logger.error(f"Error ensuring template_usage table exists: {e}")
            raise

    async def record_template_usage(self, user_id: uuid.UUID, template_id: uuid.UUID):
        if not template_id or not user_id:
            return
        try:
            await self._ensure_template_usage_table()
            async with self.get_connection() as conn:
                await conn.execute(
                    """
                    INSERT INTO template_usage (template_id, user_id, usage_count, last_used_at)
                    VALUES ($1, $2, 1, NOW())
                    ON CONFLICT (template_id, user_id)
                    DO UPDATE SET
                        usage_count = template_usage.usage_count + 1,
                        last_used_at = NOW()
                    """,
                    template_id,
                    user_id
                )
        except Exception as e:
            logger.warning(f"Error recording template usage for template {template_id}: {e}")

    async def _cleanup_template_usage(self, template_id: uuid.UUID, user_id: uuid.UUID):
        if not template_id or not self._template_usage_ready:
            return
        try:
            async with self.get_connection() as conn:
                await conn.execute(
                    "DELETE FROM template_usage WHERE template_id = $1 AND user_id = $2",
                    template_id,
                    user_id
                )
        except Exception as e:
            logger.warning(f"Error cleaning template usage for template {template_id}: {e}")

    async def get_template_insights(self, user_id: uuid.UUID) -> Dict[str, Any]:
        await self._ensure_template_usage_table()
        try:
            async with self.get_connection() as conn:
                totals = await conn.fetchrow(
                    """
                    SELECT
                        COUNT(*) AS total,
                        COUNT(*) FILTER (WHERE updated_at >= NOW() - INTERVAL '30 days') AS updated_recent,
                        MAX(updated_at) AS last_updated
                    FROM templates
                    WHERE user_id = $1
                    """,
                    user_id
                ) or {}

                usage_totals = await conn.fetchrow(
                    "SELECT COALESCE(SUM(usage_count), 0) AS usage_events FROM template_usage WHERE user_id = $1",
                    user_id
                ) or {}

                suggestions = await conn.fetch(
                    """
                    SELECT
                        t.id,
                        t.title,
                        t.category,
                        t.updated_at,
                        COALESCE(u.usage_count, 0) AS usage_count
                    FROM templates t
                    LEFT JOIN template_usage u
                      ON u.template_id = t.id AND u.user_id = $1
                    WHERE t.user_id = $1
                    ORDER BY COALESCE(u.usage_count, 0) DESC, t.updated_at DESC NULLS LAST
                    LIMIT 5
                    """,
                    user_id
                )

                categories = await conn.fetch(
                    """
                    SELECT
                        COALESCE(category, 'Allgemein') AS label,
                        COUNT(*) AS count
                    FROM templates
                    WHERE user_id = $1
                    GROUP BY COALESCE(category, 'Allgemein')
                    ORDER BY COUNT(*) DESC, label ASC
                    LIMIT 6
                    """,
                    user_id
                )

                recent_templates = await conn.fetch(
                    """
                    SELECT id, title, content, category, type, created_at, updated_at
                    FROM templates
                    WHERE user_id = $1
                    ORDER BY updated_at DESC NULLS LAST, created_at DESC
                    LIMIT 5
                    """,
                    user_id
                )

            total_templates = int(totals.get("total") or 0)
            updated_recent = int(totals.get("updated_recent") or 0)
            last_updated = totals.get("last_updated")
            usage_events = int(usage_totals.get("usage_events") or 0)

            suggestion_rows = []
            max_usage = 0
            for row in suggestions or []:
                data = dict(row)
                usage_count = int(data.get("usage_count") or 0)
                max_usage = max(max_usage, usage_count)
                suggestion_rows.append({
                    "id": str(data.get("id")),
                    "name": data.get("title") or "Vorlage",
                    "category": data.get("category"),
                    "updated_at": data.get("updated_at"),
                    "usage_count": usage_count
                })

            def compute_match(usage: int) -> int:
                if max_usage <= 0:
                    return 35
                ratio = usage / max_usage
                return min(100, max(40, int(40 + ratio * 60)))

            suggestions_payload = [
                {
                    **item,
                    "match_score": compute_match(item["usage_count"])
                }
                for item in suggestion_rows
            ]

            categories_payload = [
                {"label": row["label"], "count": int(row["count"])}
                for row in categories or []
            ]

            recent_payload = []
            for row in recent_templates or []:
                data = dict(row)
                data["id"] = str(data.get("id"))
                recent_payload.append(data)

            return {
                "counts": {
                    "active": total_templates,
                    "updated_recent": updated_recent,
                    "usage_events": usage_events
                },
                "last_updated_at": last_updated,
                "suggestions": suggestions_payload,
                "top_categories": categories_payload,
                "recent_templates": recent_payload
            }
        except Exception as e:
            logger.error(f"Error computing template insights for user {user_id}: {e}")
            return {
                "counts": {
                    "active": 0,
                    "updated_recent": 0,
                    "usage_events": 0
                },
                "last_updated_at": None,
                "suggestions": [],
                "top_categories": [],
                "recent_templates": []
            }
    # Clause methods
    async def get_clauses(
        self,
        user_id: uuid.UUID,
        category: str = None,
        language: str = None
    ):
        """Get clauses for user"""
        try:
            async with self.get_connection() as conn:
                query = "SELECT * FROM clauses WHERE user_id = $1"
                params: list[Any] = [user_id]

                if category:
                    query += " AND category = $2"
                    params.append(category)
                    if language:
                        query += " AND language = $3"
                        params.append(language)
                elif language:
                    query += " AND language = $2"
                    params.append(language)

                query += " ORDER BY created_at DESC"

                rows = await conn.fetch(query, *params)
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting clauses for user {user_id}: {e}")
            return []

    async def create_clause(
        self,
        user_id: uuid.UUID,
        title: str,
        content: str,
        category: str = None,
        language: str = None
    ):
        """Create a new clause"""
        try:
            async with self.get_connection() as conn:
                clause_id = uuid.uuid4()
                created_at = datetime.utcnow()
                await conn.execute(
                    """INSERT INTO clauses (id, user_id, title, content, category, language, created_at)
                       VALUES ($1, $2, $3, $4, $5, $6, $7)""",
                    clause_id, user_id, title, content, category, language, created_at
                )
                return {
                    "id": str(clause_id),
                    "title": title,
                    "content": content,
                    "category": category,
                    "language": language,
                    "created_at": created_at,
                }
        except Exception as e:
            logger.error(f"Error creating clause for user {user_id}: {e}")
            raise

    # Clipboard methods
    async def get_clipboard_entries(self, user_id: uuid.UUID, limit: int = 50):
        """Get clipboard entries for user"""
        try:
            async with self.get_connection() as conn:
                rows = await conn.fetch(
                    "SELECT * FROM clipboard_entries WHERE user_id = $1 ORDER BY created_at DESC LIMIT $2",
                    user_id, limit
                )
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting clipboard entries for user {user_id}: {e}")
            return []

    async def create_clipboard_entry(
        self,
        user_id: uuid.UUID,
        content: str,
        entry_type: str = "text"
    ):
        """Create a new clipboard entry"""
        try:
            async with self.get_connection() as conn:
                entry_id = uuid.uuid4()
                await conn.execute(
                    """INSERT INTO clipboard_entries (id, user_id, content, type, created_at)
                       VALUES ($1, $2, $3, $4, $5)""",
                    entry_id, user_id, content, entry_type, datetime.utcnow()
                )
                return {"id": str(entry_id), "content": content, "type": entry_type}
        except Exception as e:
            logger.error(f"Error creating clipboard entry for user {user_id}: {e}")
            raise

    # Analytics methods
    async def create_analytics_event(
        self,
        user_id: uuid.UUID,
        event_type: str,
        data: dict = None
    ):
        """Create an analytics event"""
        try:
            async with self.get_connection() as conn:
                event_id = uuid.uuid4()
                await conn.execute(
                    """INSERT INTO analytics_events (id, user_id, event_type, data, created_at)
                       VALUES ($1, $2, $3, $4, $5)""",
                    event_id, user_id, event_type, json.dumps(data) if data else None, datetime.utcnow()
                )
                return {"id": str(event_id)}
        except Exception as e:
            logger.error(f"Error creating analytics event for user {user_id}: {e}")
            raise

    # Document methods
    async def create_document(
        self,
        user_id: uuid.UUID,
        title: str,
        content: str,
        document_type: str = None
    ):
        """Create a new document"""
        try:
            async with self.get_connection() as conn:
                doc_id = uuid.uuid4()
                created_at = datetime.utcnow()
                await conn.execute(
                    """INSERT INTO documents (id, user_id, title, content, type, created_at)
                       VALUES ($1, $2, $3, $4, $5, $6)""",
                    doc_id, user_id, title, content, document_type, created_at
                )
                return {
                    "id": str(doc_id),
                    "title": title,
                    "content": content,
                    "type": document_type,
                    "document_type": document_type,
                    "created_at": created_at,
                }
        except Exception as e:
            logger.error(f"Error creating document for user {user_id}: {e}")
            raise

    # API Token methods
    async def list_api_tokens(self, user_id: uuid.UUID):
        """List API tokens for user"""
        try:
            async with self.get_connection() as conn:
                rows = await conn.fetch(
                    """SELECT id, last4, expires_at, created_at, revoked_at, last_used_at
                       FROM api_tokens
                       WHERE user_id = $1
                       ORDER BY created_at DESC""",
                    user_id
                )
                tokens: List[Dict[str, Any]] = []
                for row in rows:
                    data = dict(row)
                    data["active"] = row["revoked_at"] is None and (row["expires_at"] is None or row["expires_at"] > datetime.utcnow())
                    tokens.append(data)
                return tokens
        except Exception as e:
            logger.error(f"Error listing API tokens for user {user_id}: {e}")
            return []

    async def create_api_token(
        self,
        user_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
        last4: str
    ):
        """Create a new API token"""
        try:
            async with self.get_connection() as conn:
                token_id = uuid.uuid4()
                created_at = datetime.utcnow()
                await conn.execute(
                    """INSERT INTO api_tokens (id, user_id, token_hash, last4, expires_at, created_at)
                       VALUES ($1, $2, $3, $4, $5, $6)""",
                    token_id, user_id, token_hash, last4, expires_at, created_at
                )
                return {"id": str(token_id), "last4": last4, "expires_at": expires_at, "created_at": created_at}
        except Exception as e:
            logger.error(f"Error creating API token for user {user_id}: {e}")
            raise

    async def revoke_api_token(self, user_id: uuid.UUID, token_id: uuid.UUID):
        """Revoke an API token"""
        try:
            async with self.get_connection() as conn:
                result = await conn.execute(
                    "UPDATE api_tokens SET revoked_at = $1 WHERE id = $2 AND user_id = $3",
                    datetime.utcnow(), token_id, user_id
                )
                return result == "UPDATE 1"
        except Exception as e:
            logger.error(f"Error revoking API token {token_id}: {e}")
            return False

    async def get_api_token_owner(self, token: str):
        """Get the owner of an API token"""
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        try:
            async with self.get_connection() as conn:
                row = await conn.fetchrow(
                    """SELECT u.id, u.email, u.name, u.role, u.password_hash, u.created_at, u.is_active, t.id AS token_id
                       FROM users u
                       JOIN api_tokens t ON u.id = t.user_id
                       WHERE t.token_hash = $1 AND t.revoked_at IS NULL AND (t.expires_at IS NULL OR t.expires_at > $2)""",
                    token_hash, datetime.utcnow()
                )
                if row:
                    await conn.execute(
                        "UPDATE api_tokens SET last_used_at = NOW() WHERE id = $1",
                        row["token_id"],
                    )
                    payload = dict(row)
                    payload.pop("token_id", None)
                    return UserInDB(**payload)
                return None
        except Exception as e:
            logger.error(f"Error getting API token owner: {e}")
            return None

    # Call request methods
    async def create_call_request(self, name: str, phone: str, email: str = None, message: str = None):
        """Create a call request"""
        try:
            async with self.get_connection() as conn:
                request_id = uuid.uuid4()
                await conn.execute(
                    """INSERT INTO call_requests (id, name, phone, email, message, created_at)
                       VALUES ($1, $2, $3, $4, $5, $6)""",
                    request_id, name, phone, email, message, datetime.utcnow()
                )
                return {
                    "id": str(request_id),
                    "name": name,
                    "phone": phone,
                    "email": email,
                    "message": message,
                }
        except Exception as e:
            logger.error(f"Error creating call request: {e}")
            raise

    # Assistant conversation methods
    async def create_conversation_message(
        self,
        user_id: uuid.UUID,
        role: str,
        content: str,
        conversation_id: Optional[uuid.UUID] = None,
        model: Optional[str] = None
    ):
        """Create a new conversation message (user or assistant)"""
        try:
            async with self.get_connection() as conn:
                message_id = uuid.uuid4()
                # Generate new conversation_id if not provided
                if conversation_id is None:
                    conversation_id = uuid.uuid4()
                
                await conn.execute(
                    """INSERT INTO assistant_messages (id, conversation_id, user_id, role, content, model, created_at)
                       VALUES ($1, $2, $3, $4, $5, $6, $7)""",
                    message_id, conversation_id, user_id, role, content, model, datetime.utcnow()
                )
                return {
                    "message_id": str(message_id),
                    "conversation_id": str(conversation_id),
                    "created_at": datetime.utcnow()
                }
        except Exception as e:
            logger.error(f"Error creating conversation message for user {user_id}: {e}")
            raise

    async def get_conversation_history(
        self,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID,
        limit: int = 50
    ):
        """Get conversation history for a specific conversation"""
        try:
            async with self.get_connection() as conn:
                # Verify conversation belongs to user (security check)
                rows = await conn.fetch(
                    """SELECT id, role, content, model, created_at
                       FROM assistant_messages
                       WHERE conversation_id = $1 AND user_id = $2
                       ORDER BY created_at ASC
                       LIMIT $3""",
                    conversation_id, user_id, limit
                )
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting conversation history for {conversation_id}: {e}")
            return []

    async def get_user_conversations(
        self,
        user_id: uuid.UUID,
        limit: int = 20
    ):
        """Get list of user's conversations with last message preview"""
        try:
            async with self.get_connection() as conn:
                rows = await conn.fetch(
                    """SELECT DISTINCT ON (conversation_id)
                           conversation_id,
                           content,
                           created_at
                       FROM assistant_messages
                       WHERE user_id = $1 AND conversation_id IS NOT NULL
                       ORDER BY conversation_id, created_at DESC
                       LIMIT $2""",
                    user_id, limit
                )
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error getting conversations for user {user_id}: {e}")
            return []

    async def _ensure_chat_schema(self):
        if self._chat_schema_ready:
            return
        try:
            async with self.get_connection() as conn:
                await conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS chat_sessions (
                        id UUID PRIMARY KEY,
                        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        title TEXT,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
                await conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS chat_messages (
                        id UUID PRIMARY KEY,
                        session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
                        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        role VARCHAR(20) NOT NULL,
                        content TEXT NOT NULL,
                        metadata JSONB DEFAULT '{}'::jsonb,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
                await conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_chat_messages_session_created_at
                        ON chat_messages (session_id, created_at)
                    """
                )
            self._chat_schema_ready = True
        except Exception as e:
            logger.error(f"Error ensuring chat schema: {e}")
            raise

    async def _ensure_email_summary_schema(self):
        if self._email_summary_schema_ready:
            return
        try:
            async with self.get_connection() as conn:
                await conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS email_summaries (
                        email_id TEXT PRIMARY KEY,
                        user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        summary JSONB NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    )
                    """
                )
                await conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_email_summaries_user
                        ON email_summaries (user_id)
                    """
                )
            self._email_summary_schema_ready = True
        except Exception as e:
            logger.error(f"Error ensuring email summary schema: {e}")
            raise

    async def get_or_create_chat_session(
        self,
        user_id: uuid.UUID,
        session_id: Optional[uuid.UUID] = None,
        title: Optional[str] = None
    ) -> uuid.UUID:
        await self._ensure_chat_schema()
        try:
            async with self.get_connection() as conn:
                if session_id:
                    row = await conn.fetchrow(
                        "SELECT id FROM chat_sessions WHERE id = $1 AND user_id = $2",
                        session_id,
                        user_id,
                    )
                    if row:
                        await conn.execute(
                            "UPDATE chat_sessions SET updated_at = NOW() WHERE id = $1",
                            row["id"],
                        )
                        return row["id"]

                new_id = session_id or uuid.uuid4()
                await conn.execute(
                    """
                    INSERT INTO chat_sessions (id, user_id, title)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (id)
                    DO UPDATE SET
                        updated_at = NOW(),
                        title = COALESCE(EXCLUDED.title, chat_sessions.title)
                    """,
                    new_id,
                    user_id,
                    title,
                )
                return new_id
        except Exception as e:
            logger.error(f"Error creating chat session for user {user_id}: {e}")
            raise

    async def add_chat_message(
        self,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> uuid.UUID:
        await self._ensure_chat_schema()
        message_id = uuid.uuid4()
        try:
            async with self.get_connection() as conn:
                await conn.execute(
                    """
                    INSERT INTO chat_messages (id, session_id, user_id, role, content, metadata)
                    VALUES ($1, $2, $3, $4, $5, $6)
                    """,
                    message_id,
                    session_id,
                    user_id,
                    role,
                    content,
                    json.dumps(metadata or {}),
                )
                await conn.execute(
                    """
                    UPDATE chat_sessions
                    SET updated_at = NOW(),
                        title = COALESCE(title, NULLIF($2, ''))
                    WHERE id = $1
                    """,
                    session_id,
                    content[:120],
                )
            return message_id
        except Exception as e:
            logger.error(f"Error adding chat message for session {session_id}: {e}")
            raise

    async def get_chat_history(
        self,
        session_id: uuid.UUID,
        user_id: uuid.UUID,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        await self._ensure_chat_schema()
        try:
            async with self.get_connection() as conn:
                rows = await conn.fetch(
                    """
                    SELECT id, role, content, metadata, created_at
                    FROM chat_messages
                    WHERE session_id = $1 AND user_id = $2
                    ORDER BY created_at ASC
                    LIMIT $3
                    """,
                    session_id,
                    user_id,
                    limit,
                )
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"Error loading chat history for session {session_id}: {e}")
            return []

    async def upsert_email_summary(
        self,
        user_id: uuid.UUID,
        email_id: str,
        summary: Dict[str, Any],
    ):
        await self._ensure_email_summary_schema()
        try:
            async with self.get_connection() as conn:
                await conn.execute(
                    """
                    INSERT INTO email_summaries (email_id, user_id, summary, created_at)
                    VALUES ($1, $2, $3::jsonb, NOW())
                    ON CONFLICT (email_id)
                    DO UPDATE SET
                        user_id = EXCLUDED.user_id,
                        summary = EXCLUDED.summary,
                        created_at = NOW()
                    """,
                    email_id,
                    user_id,
                    json.dumps(summary),
                )
        except Exception as e:
            logger.error(f"Error upserting email summary for {email_id}: {e}")
            raise

    async def get_email_summary(
        self,
        user_id: uuid.UUID,
        email_id: str,
    ) -> Optional[Dict[str, Any]]:
        await self._ensure_email_summary_schema()
        try:
            async with self.get_connection() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT summary, created_at
                    FROM email_summaries
                    WHERE email_id = $1 AND user_id = $2
                    """,
                    email_id,
                    user_id,
                )
                if row:
                    payload = dict(row)
                    payload["summary"] = dict(payload.get("summary") or {})
                    return payload
                return None
        except Exception as e:
            logger.error(f"Error fetching email summary for {email_id}: {e}")
            return None

    # ========================================================================
    # Dashboard Query Methods
    # ========================================================================

    async def get_user_dashboard_stats(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """
        Get dashboard statistics for a user (counts of cases, documents, emails).
        Returns a dict with: newCases, documents, emails, nextDeadline
        """
        try:
            async with self.get_connection() as conn:
                # Count new cases (created in last 30 days)
                new_cases_count = await conn.fetchval(
                    """
                    SELECT COUNT(*) FROM cases 
                    WHERE user_id = $1 
                    AND created_at >= NOW() - INTERVAL '30 days'
                    """,
                    user_id
                ) or 0

                # Count total documents for user
                documents_count = await conn.fetchval(
                    """
                    SELECT COUNT(*) FROM documents 
                    WHERE user_id = $1
                    """,
                    user_id
                ) or 0

                # Count total emails (from activities table)
                emails_count = await conn.fetchval(
                    """
                    SELECT COUNT(*) FROM activities 
                    WHERE user_id = $1 AND activity_type = 'email'
                    """,
                    user_id
                ) or 0

                # Get next upcoming deadline
                next_deadline_row = await conn.fetchrow(
                    """
                    SELECT due_date FROM deadlines 
                    WHERE user_id = $1 
                    AND completed = FALSE 
                    AND due_date >= NOW()
                    ORDER BY due_date ASC 
                    LIMIT 1
                    """,
                    user_id
                )
                next_deadline = next_deadline_row["due_date"].isoformat() if next_deadline_row else None

                return {
                    "newCases": int(new_cases_count),
                    "documents": int(documents_count),
                    "emails": int(emails_count),
                    "nextDeadline": next_deadline
                }
        except Exception as e:
            logger.error(f"Error fetching dashboard stats for user {user_id}: {e}")
            # Return zeros on error (graceful degradation)
            return {
                "newCases": 0,
                "documents": 0,
                "emails": 0,
                "nextDeadline": None
            }

    async def get_user_recent_documents(self, user_id: uuid.UUID, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Get user's most recent documents with metadata.
        Returns list of dicts with: id, title, updated_at, status, progress, details
        """
        try:
            async with self.get_connection() as conn:
                rows = await conn.fetch(
                    """
                    SELECT 
                        id, 
                        title, 
                        updated_at, 
                        status, 
                        progress,
                        created_at
                    FROM documents 
                    WHERE user_id = $1
                    ORDER BY updated_at DESC NULLS LAST, created_at DESC
                    LIMIT $2
                    """,
                    user_id,
                    limit
                )
                
                documents = []
                for row in rows:
                    # Calculate updated label (e.g., "vor 2 Stunden")
                    updated_at = row["updated_at"] or row["created_at"]
                    
                    doc = {
                        "id": str(row["id"]),
                        "title": row["title"] or "Unbenanntes Dokument",
                        "updated_at": updated_at.isoformat() if updated_at else None,
                        "status": row["status"] or "draft",
                        "progress": row["progress"] or 0,
                        "details": f"Zuletzt ge?ndert ? Version 1"
                    }
                    
                    # Determine status type for badge rendering
                    status = row["status"] or "draft"
                    if status == "final":
                        doc["statusType"] = "final"
                    elif row["progress"] and row["progress"] > 0:
                        doc["statusType"] = "progress"
                    else:
                        doc["statusType"] = "review"
                    
                    documents.append(doc)
                
                return documents
        except Exception as e:
            logger.error(f"Error fetching recent documents for user {user_id}: {e}")
            return []

    async def get_user_upcoming_deadlines(self, user_id: uuid.UUID, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Get user's upcoming deadlines sorted by due date.
        Returns list of dicts with: id, title, description, due_date, priority
        """
        try:
            async with self.get_connection() as conn:
                rows = await conn.fetch(
                    """
                    SELECT 
                        id, 
                        title, 
                        description, 
                        due_date, 
                        priority
                    FROM deadlines 
                    WHERE user_id = $1 
                    AND completed = FALSE
                    AND due_date >= NOW()
                    ORDER BY due_date ASC
                    LIMIT $2
                    """,
                    user_id,
                    limit
                )
                
                deadlines = []
                for row in rows:
                    deadlines.append({
                        "id": str(row["id"]),
                        "title": row["title"],
                        "description": row["description"] or "",
                        "due_date": row["due_date"].isoformat(),
                        "priority": row["priority"] or "medium"
                    })
                
                return deadlines
        except Exception as e:
            logger.error(f"Error fetching upcoming deadlines for user {user_id}: {e}")
            return []

    async def get_user_recent_activity(self, user_id: uuid.UUID, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Get user's recent activity (emails, calls, uploads, etc.).
        Returns list of dicts with: id, type, title, description, status, created_at
        """
        try:
            async with self.get_connection() as conn:
                rows = await conn.fetch(
                    """
                    SELECT 
                        id, 
                        activity_type, 
                        title, 
                        description, 
                        status, 
                        created_at,
                        metadata
                    FROM activities 
                    WHERE user_id = $1
                    ORDER BY created_at DESC
                    LIMIT $2
                    """,
                    user_id,
                    limit
                )
                
                activities = []
                for row in rows:
                    activity = {
                        "id": str(row["id"]),
                        "type": row["activity_type"],
                        "title": row["title"],
                        "description": row["description"] or "",
                        "status": row["status"] or "pending",
                        "created_at": row["created_at"].isoformat(),
                    }
                    
                    # Extract client name from description if available
                    if row["description"]:
                        activity["client"] = row["description"].split(" ")[0] if " " in row["description"] else ""
                    else:
                        activity["client"] = ""
                    
                    # Add metadata if present
                    if row["metadata"]:
                        activity["metadata"] = dict(row["metadata"])
                    
                    activities.append(activity)
                
                return activities
        except Exception as e:
            logger.error(f"Error fetching recent activity for user {user_id}: {e}")
            return []

    async def get_user_continue_suggestion(self, user_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        """
        Get suggestion for "continue working on" bar (in-progress document with highest completion).
        Returns dict with: id, title, progress, deadline or None if no in-progress documents.
        """
        try:
            async with self.get_connection() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT 
                        d.id, 
                        d.title, 
                        d.progress,
                        MIN(dl.due_date) as nearest_deadline
                    FROM documents d
                    LEFT JOIN deadlines dl ON dl.user_id = d.user_id AND dl.completed = FALSE
                    WHERE d.user_id = $1
                    AND d.status = 'in_progress'
                    AND d.progress > 0
                    AND d.progress < 100
                    GROUP BY d.id, d.title, d.progress
                    ORDER BY d.progress DESC, d.updated_at DESC
                    LIMIT 1
                    """,
                    user_id
                )
                
                if row:
                    return {
                        "id": str(row["id"]),
                        "title": row["title"],
                        "progress": row["progress"] or 0,
                        "deadline": row["nearest_deadline"].isoformat() if row["nearest_deadline"] else None
                    }
                return None
        except Exception as e:
            logger.error(f"Error fetching continue suggestion for user {user_id}: {e}")
            return None

# Simple user model class to avoid circular imports
class UserInDB:
    def __init__(
        self,
        id,
        email,
        name,
        role,
        password_hash,
        created_at,
        is_active: Optional[bool] = None
    ):
        self.id = id
        self.email = email
        self.name = name
        self.role = role
        self.password_hash = password_hash
        self.created_at = created_at
        self.is_active = True if is_active is None else bool(is_active)

def get_database():
    """Dependency function to get database instance"""
    # This would typically return a singleton instance
    # For now, we'll assume the database instance is available globally
    return None  # This will be replaced by the actual instance
