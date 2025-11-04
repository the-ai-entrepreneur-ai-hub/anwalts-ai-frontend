import os
import sys
import uuid
import importlib.util
import types
from collections.abc import Mapping, Iterator

import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

from database import Database

_BACKEND_PATH = os.path.join(ROOT_DIR, 'backend-main.py')


class _SupabaseClientStub:  # pragma: no cover - simple import shim
    pass


def _supabase_create_client_stub(url, key):  # pragma: no cover - simple import shim
    return _SupabaseClientStub()


sys.modules.setdefault(
    'supabase',
    types.SimpleNamespace(Client=_SupabaseClientStub, create_client=_supabase_create_client_stub),
)

_backend_spec = importlib.util.spec_from_file_location("backend_main_for_email_status", _BACKEND_PATH)
backend = importlib.util.module_from_spec(_backend_spec)  # type: ignore
assert _backend_spec and _backend_spec.loader
_backend_spec.loader.exec_module(backend)  # type: ignore


class DummyRecord(Mapping):
    """Lightweight asyncpg.Record stand-in that lacks dict helpers like .get."""

    def __init__(self, data: dict):
        self._data = dict(data)

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self) -> Iterator:
        return iter(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def items(self):
        return self._data.items()

    def keys(self):
        return self._data.keys()


class FakeConn:
    def __init__(self, *, user_email: str, user_id: uuid.UUID, existing_account=None):
        self.user_email = user_email
        self.user_id = user_id
        self.existing_account = existing_account
        self.account_rows_by_id = {}
        if existing_account:
            self.account_rows_by_id[existing_account["id"]] = existing_account
        self.queries = []

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def fetchrow(self, query, *params):
        self.queries.append(("fetchrow", query, params))
        lowered = " ".join(query.lower().split())
        if "select email from users" in lowered:
            return {"email": self.user_email}
        if "select * from email_accounts where user_id" in lowered:
            return self.existing_account
        if "select * from email_accounts where id" in lowered:
            account_id = params[0]
            return self.account_rows_by_id.get(account_id)
        if "select active_account_id" in lowered:
            return None
        return None

    async def fetchval(self, query, *params):
        self.queries.append(("fetchval", query, params))
        return 0

    async def execute(self, query, *params):
        self.queries.append(("execute", query, params))
        lowered = " ".join(query.lower().split())
        if "insert into email_accounts" in lowered:
            account_id = params[0]
            self.account_rows_by_id[account_id] = {
                "id": account_id,
                "user_id": params[1],
                "provider": params[2],
                "email_address": params[3],
                "display_name": params[4],
                "login_email_snapshot": params[5],
                "link_source": params[6],
                "refresh_token_encrypted": params[7],
                "is_primary": params[9],
                "oauth_consent": params[10] if params[10] is not None else False,
                "ai_read_consent": params[11] if params[11] is not None else False,
                "draft_only_mode": params[12] if params[12] is not None else True,
                "consent_timestamp": params[13],
                "ai_consent_revoked_at": None,
                "last_consent_update": None,
                "linked_at": params[14],
                "last_connected_at": params[15],
                "revoked_at": None,
                "updated_at": params[15],
                "scopes": params[8],
            }
        elif "update email_accounts" in lowered and self.existing_account:
            updated = dict(self.existing_account)
            consent_timestamp = params[8]
            consent_updated = params[9]
            updated_at = params[10]
            last_connected = params[11]
            if consent_updated:
                updated_last_consent = updated_at
            else:
                updated_last_consent = updated.get("last_consent_update")
            updated.update(
                display_name=params[0],
                login_email_snapshot=params[1],
                link_source=params[2],
                refresh_token_encrypted=params[3],
                scopes=params[4],
                oauth_consent=params[5],
                ai_read_consent=params[6],
                draft_only_mode=params[7],
                consent_timestamp=consent_timestamp,
                last_consent_update=updated_last_consent,
                last_connected_at=last_connected,
                updated_at=updated_at,
            )
            self.existing_account = updated
            self.account_rows_by_id[updated["id"]] = updated
        return "OK"


@pytest.fixture(autouse=True)
def _email_secret_env(monkeypatch):
    monkeypatch.setenv("EMAIL_ACCOUNT_SECRET", "0" * 32)


@pytest.mark.asyncio
async def test_upsert_email_account_allows_login_email_for_oauth(monkeypatch):
    db = Database()
    db.pool = object()
    user_id = uuid.uuid4()
    fake_conn = FakeConn(user_email="user@example.com", user_id=user_id)

    monkeypatch.setattr(db, "get_connection", lambda: fake_conn)
    monkeypatch.setattr(db, "_encrypt_refresh_token", lambda token: f"enc:{token}")

    account = await db.upsert_email_account(
        user_id=user_id,
        provider="google",
        email_address="user@example.com",
        display_name="User",
        refresh_token="token",
        link_source="oauth",
    )

    assert account["email_address"] == "user@example.com"
    assert account["link_source"] == "oauth"


@pytest.mark.asyncio
async def test_upsert_email_account_allows_login_source(monkeypatch):
    db = Database()
    db.pool = object()
    user_id = uuid.uuid4()
    fake_conn = FakeConn(user_email="user@example.com", user_id=user_id)

    monkeypatch.setattr(db, "get_connection", lambda: fake_conn)
    monkeypatch.setattr(db, "_encrypt_refresh_token", lambda token: f"enc:{token}")

    account = await db.upsert_email_account(
        user_id=user_id,
        provider="google",
        email_address="user@example.com",
        display_name="User",
        refresh_token="token",
        link_source="login",
    )

    assert account["email_address"] == "user@example.com"
    assert account["link_source"] == "login"
    assert account["login_email_snapshot"] is None


@pytest.mark.asyncio
async def test_upsert_email_account_preserves_legacy_accounts(monkeypatch):
    db = Database()
    db.pool = object()
    user_id = uuid.uuid4()
    account_id = uuid.uuid4()
    existing = {
        "id": account_id,
        "user_id": user_id,
        "provider": "google",
        "email_address": "user@example.com",
        "display_name": "Existing",
        "login_email_snapshot": "user@example.com",
        "link_source": "legacy",
        "refresh_token_encrypted": "enc:old",
        "scopes": ["scope"],
        "is_primary": True,
        "oauth_consent": True,
        "ai_read_consent": True,
        "draft_only_mode": False,
        "consent_timestamp": None,
        "ai_consent_revoked_at": None,
        "last_consent_update": None,
        "linked_at": None,
        "last_connected_at": None,
        "revoked_at": None,
        "updated_at": None,
    }
    fake_conn = FakeConn(user_email="user@example.com", user_id=user_id, existing_account=existing)

    monkeypatch.setattr(db, "get_connection", lambda: fake_conn)
    monkeypatch.setattr(db, "_encrypt_refresh_token", lambda token: f"enc:{token}")

    account = await db.upsert_email_account(
        user_id=user_id,
        provider="google",
        email_address="user@example.com",
        display_name="Updated",
        refresh_token="token",
    )

    assert account["link_source"] == "legacy"
    assert account["display_name"] == "Updated"
    assert account["email_address"] == "user@example.com"


@pytest.mark.asyncio
async def test_set_gmail_refresh_token_forces_full_access(monkeypatch):
    db = Database()
    user_id = uuid.uuid4()
    captured = {}

    async def fake_pending(user_id):
        return {
            "oauth_consent": True,
            "ai_read_consent": True,
            "draft_only_mode": True,
        }

    async def fake_upsert(**kwargs):
        captured.update(kwargs)
        return {
            "id": uuid.uuid4(),
            "oauth_consent": True,
            "ai_read_consent": True,
            "draft_only_mode": kwargs.get("draft_only_mode"),
        }

    async def fake_clear(_user_id):
        return None

    monkeypatch.setattr(db, "get_pending_gmail_consent", fake_pending)
    monkeypatch.setattr(db, "upsert_email_account", fake_upsert)
    monkeypatch.setattr(db, "clear_pending_gmail_consent", fake_clear)

    account = await db.set_gmail_refresh_token(
        user_id=user_id,
        refresh_token="token",
        email_address="user@example.com",
        display_name="User",
        scopes=["scope"],
        oauth_consent=True,
        ai_read_consent=True,
    )

    assert account is not None
    assert captured.get("draft_only_mode") is False


@pytest.mark.asyncio
async def test_set_gmail_consent_disables_draft_only(monkeypatch):
    db = Database()
    user_id = uuid.uuid4()
    account_id = uuid.uuid4()
    captured = {}

    async def fake_get_active(_user_id):
        return {
            "id": account_id,
            "email_address": "user@example.com",
            "display_name": "User",
            "scopes": ["scope"],
            "draft_only_mode": True,
            "link_source": "oauth",
        }

    async def fake_get_refresh(_user_id, _account_id):
        return "refresh-token"

    async def fake_upsert(**kwargs):
        captured.update(kwargs)
        return {}

    monkeypatch.setattr(db, "get_active_email_account", fake_get_active)
    monkeypatch.setattr(db, "get_email_account_refresh_token", fake_get_refresh)
    monkeypatch.setattr(db, "upsert_email_account", fake_upsert)

    result = await db.set_gmail_consent(
        user_id=user_id,
        oauth_consent=True,
        ai_read_consent=True,
    )

    assert result is True
    assert captured.get("draft_only_mode") is False


def test_normalize_gmail_status_handles_records():
    user_id = uuid.uuid4()
    now = backend.datetime.utcnow()
    record_payload = {
        "id": uuid.uuid4(),
        "email_address": "lawyer@example.com",
        "oauth_consent": 1,
        "ai_read_consent": 1,
        "draft_only_mode": 0,
        "linked_at": now,
        "consent_timestamp": now,
    }
    raw_status = {
        "active_account": DummyRecord(record_payload),
        "accounts": [DummyRecord(record_payload)],
    }

    normalised, flags = backend._normalize_gmail_status(raw_status, user_id)

    assert normalised["connected"] is True
    assert normalised["active_account"]["email_address"] == "lawyer@example.com"
    assert normalised["active_account"]["draft_only_mode"] is False
    assert normalised["accounts"][0]["is_active"] is True
    assert flags["active_sanitised"] is True
    assert flags["accounts_sanitised"] == 1


@pytest.mark.asyncio
async def test_get_gmail_connection_status_returns_plain_dict(monkeypatch):
    user_id = uuid.uuid4()
    db = Database()
    account = DummyRecord({
        "id": uuid.uuid4(),
        "user_id": user_id,
        "provider": "google",
        "email_address": "lawyer@example.com",
        "display_name": "Lawyer",
        "oauth_consent": True,
        "ai_read_consent": True,
        "draft_only_mode": False,
        "linked_at": backend.datetime.utcnow(),
    })

    async def fake_list(_user_id):
        return [account]

    async def fake_active(_user_id):
        return account

    monkeypatch.setattr(db, "list_email_accounts", fake_list)
    monkeypatch.setattr(db, "get_active_email_account", fake_active)

    status = await db.get_gmail_connection_status(user_id)

    assert isinstance(status["active_account"], dict)
    assert status["active_account"]["email_address"] == "lawyer@example.com"
    assert status["accounts"][0]["email_address"] == "lawyer@example.com"
    assert status["connected"] is True
