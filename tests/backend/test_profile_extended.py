import os
import sys
import uuid
import asyncio

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT not in sys.path:
    sys.path.append(ROOT)

import importlib.util

_BACKEND_PATH = os.path.join(ROOT, 'backend-main.py')
spec = importlib.util.spec_from_file_location("backend_main_mod", _BACKEND_PATH)
backend = importlib.util.module_from_spec(spec)  # type: ignore
assert spec and spec.loader
spec.loader.exec_module(backend)  # type: ignore


@pytest.mark.asyncio
async def test_get_user_profile_returns_portal_identity(monkeypatch):
    # Arrange: create a fake current user
    from models import UserInDB
    from datetime import datetime

    user = UserInDB(
        id=uuid.uuid4(),
        email="custom@example.com",
        name="Custom User",
        role="assistant",
        password_hash="",
        created_at=datetime.utcnow(),
        is_active=True,
    )

    # Act
    result = await backend.get_user_profile(current_user=user)  # type: ignore

    # Assert identity fields reflect login user
    assert result.email == "custom@example.com"
    assert result.name == "Custom User"
    assert result.role == "assistant"


@pytest.mark.asyncio
async def test_get_user_profile_extended_includes_data(monkeypatch):
    # Arrange: fake DB returning profile data and a fake user
    class FakeDB:
        async def get_user_profile(self, user_id):
            return {"user_id": user_id, "data": {"company": "ACME", "phone": "+49 30 123"}}

    backend.db = FakeDB()  # type: ignore

    from models import UserInDB
    from datetime import datetime

    user = UserInDB(
        id=uuid.uuid4(),
        email="custom@example.com",
        name="Custom User",
        role="assistant",
        password_hash="",
        created_at=datetime.utcnow(),
        is_active=True,
    )

    # Act
    ext = await backend.get_user_profile_extended(current_user=user)  # type: ignore

    # Assert: identity + data
    assert ext.email == "custom@example.com"
    assert isinstance(ext.data, dict)
    assert ext.data.get("company") == "ACME"
