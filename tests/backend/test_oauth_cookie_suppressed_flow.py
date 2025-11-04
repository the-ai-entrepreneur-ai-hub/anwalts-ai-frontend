import os
import sys
import importlib.util
import uuid
import pytest
from starlette.datastructures import URL, QueryParams

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.append(ROOT)

_BACKEND_PATH = os.path.join(ROOT, 'backend-main.py')
spec = importlib.util.spec_from_file_location("backend_main_mod", _BACKEND_PATH)
backend = importlib.util.module_from_spec(spec)  # type: ignore
assert spec and spec.loader
spec.loader.exec_module(backend)  # type: ignore


class FakeCache:
    async def get(self, key: str):
        # Simulate server-side link-user mapping present for this state
        if key.startswith("oauth:link-user:"):
            return str(uuid.uuid4())
        return None


class FakeDB:
    async def get_user_by_id(self, user_id):
        # Simulate cookie-suppressed environment where we cannot resolve user
        return None


class FakeRequest:
    def __init__(self, cookies=None, headers=None, state_value: str = "abc"):
        self._cookies = cookies or {}
        self._headers = headers or {}
        self._url = URL("https://portal-anwalts.ai/auth/google/callback")
        self._query = QueryParams({"state": state_value})

    @property
    def cookies(self):
        return self._cookies

    @property
    def headers(self):
        return self._headers

    @property
    def url(self):
        return self._url

    @property
    def query_params(self):
        return self._query


@pytest.mark.asyncio
async def test_gmail_flow_cookie_suppressed_raises_401(monkeypatch):
    # Arrange: inject fake cache and DB
    backend.cache_service = FakeCache()  # type: ignore
    backend.db = FakeDB()  # type: ignore

    request = FakeRequest(cookies={}, headers={}, state_value="state-test-1")

    # Act + Assert: callback should infer gmail mode via cache and reject with 401
    with pytest.raises(backend.HTTPException) as exc:
        await backend.google_callback(request=request, code=None, state="state-test-1")  # type: ignore

    assert exc.value.status_code == 401
    assert "Sitzung ist abgelaufen" in str(exc.value.detail)

