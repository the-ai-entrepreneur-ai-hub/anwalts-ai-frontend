import os
import sys
import importlib.util
import types
import uuid
import json
import pytest
from starlette.requests import Request
from starlette.datastructures import URL, QueryParams


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.append(ROOT)

_BACKEND_PATH = os.path.join(ROOT, 'backend-main.py')

# Provide a minimal stub for `supabase` to satisfy import-time dependency
class _SupabaseClientStub:  # pragma: no cover - simple import shim
    pass

def _supabase_create_client_stub(url, key):  # pragma: no cover - simple import shim
    return _SupabaseClientStub()

sys.modules.setdefault('supabase', types.SimpleNamespace(
    Client=_SupabaseClientStub,
    create_client=_supabase_create_client_stub,
))

spec = importlib.util.spec_from_file_location("backend_main_mod", _BACKEND_PATH)
backend = importlib.util.module_from_spec(spec)  # type: ignore
assert spec and spec.loader
spec.loader.exec_module(backend)  # type: ignore


class FakeUser:
    def __init__(self, id: str, email: str = "user@test.local", role: str = "assistant", name: str = "Test User"):
        self.id = id
        self.email = email
        self.role = role
        self.name = name


@pytest.fixture(autouse=True)
def _google_env(monkeypatch):
    # Minimal Google config for authorize + callback building
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "test-client-id")
    monkeypatch.setenv("PUBLIC_BASE_URL", "http://localhost:3000")
    monkeypatch.setenv("GOOGLE_REDIRECT_PATH", "/api/auth/google/callback")
    yield


def _install_httpx_mocks(
    monkeypatch,
    profile_email: str,
    name: str = "Test Person",
    refresh_token: str | None = "r1",
    include_gmail_scopes: bool = True,
):
    """Patch httpx.AsyncClient to simulate token + userinfo exchange."""
    class MockResponse:
        def __init__(self, status_code: int, data: dict):
            self._status = status_code
            self._data = data
            self.text = json.dumps(data)

        def raise_for_status(self):
            if not (200 <= self._status < 300):
                raise Exception(f"HTTP {self._status}")

        def json(self):
            return self._data

        @property
        def status_code(self):
            return self._status

    class MockHTTPError(Exception):
        pass

    class MockAsyncClient:
        def __init__(self, *_, **__):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        async def post(self, url, data=None, headers=None):
            # Simulate token endpoint
            scope = "openid email profile"
            if include_gmail_scopes:
                scope += " https://www.googleapis.com/auth/gmail.readonly https://www.googleapis.com/auth/gmail.modify"
            data_out = {
                "access_token": "acc-token",
                "id_token": "id-token",
                "scope": scope,
            }
            if refresh_token is not None:
                data_out["refresh_token"] = refresh_token
            return MockResponse(200, data_out)

        async def get(self, url, headers=None):
            # Simulate userinfo endpoint
            return MockResponse(200, {
                "email": profile_email,
                "name": name,
                "given_name": name.split(" ")[0],
                "family_name": name.split(" ")[-1],
            })

    monkeypatch.setattr(backend, "httpx", types.SimpleNamespace(AsyncClient=MockAsyncClient, HTTPError=MockHTTPError))


def _fake_linking_deps(monkeypatch, user_id: str = None):
    """Patch auth + db so callback can run without real services."""
    if not user_id:
        user_id = str(uuid.uuid4())

    # Return a fixed portal user to represent the currently logged-in session
    async def fake_current_user(request):
        return FakeUser(user_id)

    async def fake_set_gmail_refresh_token(uid, refresh_token, email_address, display_name, scopes=None, oauth_consent=True, link_source="oauth"):
        # Validate parameters minimally
        assert uid == user_id
        assert refresh_token
        assert email_address
        return {"id": str(uuid.uuid4())}

    async def fake_set_active_email_account(uid, account_id):
        assert uid == user_id
        assert account_id

    # DB getters used elsewhere in callback for login path (not used in linking)
    async def fake_get_user_by_email(email):
        return None

    # Install service stubs directly on backend globals (startup is not run in these tests)
    backend.db = types.SimpleNamespace(
        set_gmail_refresh_token=fake_set_gmail_refresh_token,
        set_active_email_account=fake_set_active_email_account,
        get_user_by_email=fake_get_user_by_email,
    )
    backend.auth_service = types.SimpleNamespace(
        create_access_token=lambda data: "test-jwt-token",
        verify_token=lambda token: {"sub": str(uuid.uuid4())},
    )
    monkeypatch.setattr(backend, "get_current_user_flexible", fake_current_user)


@pytest.mark.asyncio
async def test_google_authorize_sets_cookies_for_gmail_linking(monkeypatch):
    # Logged-in user is required for gmail linking mode
    fake_user_id = str(uuid.uuid4())

    async def fake_current_user(_request):
        return FakeUser(fake_user_id)

    monkeypatch.setattr(backend, "get_current_user_flexible", fake_current_user)

    # Build a minimal Request object for direct handler invocation
    scope = {
        'type': 'http',
        'method': 'GET',
        'path': '/auth/google/authorize',
        'query_string': b'mode=gmail',
        'headers': [],
        'client': ('test', 123),
        'server': ('testserver', 80),
        'scheme': 'http',
    }
    req = Request(scope)
    res = await backend.google_authorize(req)  # type: ignore

    # Validate redirect to Google and Set-Cookie headers
    assert res.status_code in (302, 307)
    assert res.headers.get("location", "").startswith("https://accounts.google.com/")

    # Collect all set-cookie headers from raw_headers to avoid merging issues
    cookies = [
        val.decode()
        for (name, val) in getattr(res, 'raw_headers', [])
        if name.decode().lower() == 'set-cookie'
    ]
    combined = "\n".join(cookies)
    assert "oauth_flow_mode=gmail" in combined
    assert "email_link_uid=" in combined


@pytest.mark.asyncio
async def test_google_callback_gmail_linking_preserves_session(monkeypatch):
    # Arrange mocks for token exchange and current session
    profile_email = "angelageneralao.1997@gmail.com"
    _install_httpx_mocks(monkeypatch, profile_email=profile_email)
    _fake_linking_deps(monkeypatch)

    # Build callback request with cookies set
    cookie_header = (
        "oauth_flow_mode=gmail; "
        f"email_link_uid={uuid.uuid4()}"
    ).encode()
    scope = {
        'type': 'http',
        'method': 'GET',
        'path': '/auth/google/callback',
        'query_string': b'code=abc&state=state1',
        'headers': [(b'cookie', cookie_header)],
        'client': ('test', 123),
        'server': ('testserver', 80),
        'scheme': 'http',
    }
    req = Request(scope)
    res = await backend.google_callback(request=req, code="abc", state="state1")  # type: ignore

    assert res.status_code == 200
    body = (res.body or b"").decode()
    assert "Gmail connected successfully" in body

    # Must NOT set auth_token in linking flow (session preserved)
    cookies = [
        val.decode()
        for (name, val) in getattr(res, 'raw_headers', [])
        if name.decode().lower() == 'set-cookie'
    ]
    combined = "\n".join(cookies)
    assert "auth_token=" not in combined
    # But should set active_email_account helper cookie
    assert "active_email_account=" in combined


@pytest.mark.asyncio
async def test_google_callback_login_flow_sets_session(monkeypatch):
    # Arrange mocks for token exchange and account creation path
    login_email = "test.reg.e2e+20251026@anwalts.ai"
    _install_httpx_mocks(monkeypatch, profile_email=login_email, refresh_token=None, include_gmail_scopes=False)

    # DB path for login: no existing user -> create user
    created_user_id = str(uuid.uuid4())

    async def fake_get_user_by_email(email):
        return None

    async def fake_create_user(email, name, role, password_hash):
        return FakeUser(created_user_id, email=email, role=role, name=name)

    # Avoid coupling to password hashing internals
    monkeypatch.setattr(backend.db, "get_user_by_email", fake_get_user_by_email, raising=False)
    monkeypatch.setattr(backend.db, "create_user", fake_create_user, raising=False)

    # Install bare db/auth stubs for login path
    backend.db = types.SimpleNamespace(
        get_user_by_email=fake_get_user_by_email,
        create_user=fake_create_user,
        set_gmail_refresh_token=lambda *args, **kwargs: None,
        set_active_email_account=lambda *args, **kwargs: None,
    )
    backend.auth_service = types.SimpleNamespace(
        create_access_token=lambda data: "test-jwt-token",
        hash_password=lambda pwd: "hash",
    )

    # Force login flow explicitly via cookie
    scope = {
        'type': 'http',
        'method': 'GET',
        'path': '/auth/google/callback',
        'query_string': b'code=abc&state=state2',
        'headers': [(b'cookie', b'oauth_flow_mode=login')],
        'client': ('test', 123),
        'server': ('testserver', 80),
        'scheme': 'http',
    }
    req = Request(scope)
    res = await backend.google_callback(request=req, code="abc", state="state2")  # type: ignore

    assert res.status_code == 200
    # Should set auth_token cookie
    cookies = [
        val.decode()
        for (name, val) in getattr(res, 'raw_headers', [])
        if name.decode().lower() == 'set-cookie'
    ]
    combined = "\n".join(cookies)
    assert "auth_token=" in combined
    body = (res.body or b"").decode()
    # Contains login HTML payload
    assert "Signing in" in body or "Signing in".lower() in body.lower()
