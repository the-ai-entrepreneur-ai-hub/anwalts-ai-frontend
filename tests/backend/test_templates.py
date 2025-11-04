import asyncio
import os
import sys
import uuid
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

import pytest

from ai_service import AIResponse, AIService
from database import Database


class FakeConn:
    def __init__(self):
        self.calls = []
        self.totals = {
            "total": 3,
            "updated_recent": 2,
            "last_updated": datetime(2024, 6, 20, 9, 0, 0),
        }
        self.usage_totals = {"usage_events": 5}
        self.suggestions = [
            {
                "id": uuid.uuid4(),
                "title": "Arbeitsvertrag",
                "category": "Arbeitsrecht",
                "updated_at": datetime(2024, 6, 20, 9, 0, 0),
                "usage_count": 4,
            }
        ]
        self.categories = [
            {"label": "Arbeitsrecht", "count": 2},
            {"label": "Vertrag", "count": 1},
        ]
        self.recent = [
            {
                "id": uuid.uuid4(),
                "title": "Aktuelle NDA",
                "content": "<p>Inhalt</p>",
                "category": "Vertrag",
                "type": "document",
                "created_at": datetime(2024, 6, 19, 8, 0, 0),
                "updated_at": datetime(2024, 6, 19, 10, 0, 0),
            }
        ]
        self.execute_result = None

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def execute(self, query, *params):
        self.calls.append(("execute", query, params))
        return self.execute_result

    async def fetchrow(self, query, *params):
        self.calls.append(("fetchrow", query, params))
        if "SUM(usage_count)" in query:
            return self.usage_totals
        return self.totals

    async def fetch(self, query, *params):
        self.calls.append(("fetch", query, params))
        if "FROM templates t" in query:
            return self.suggestions
        if "GROUP BY" in query:
            return self.categories
        return self.recent

    async def fetchval(self, query, *params):
        self.calls.append(("fetchval", query, params))
        return None


class ConnCtx:
    def __init__(self, conn):
        self.conn = conn

    async def __aenter__(self):
        return await self.conn.__aenter__()

    async def __aexit__(self, exc_type, exc, tb):
        return await self.conn.__aexit__(exc_type, exc, tb)


def test_record_template_usage_writes_upsert():
    db = Database()
    db._template_usage_ready = True

    async def noop():
        return None

    db._ensure_template_usage_table = noop  # type: ignore

    conn = FakeConn()

    def get_conn():
        return ConnCtx(conn)

    db.get_connection = get_conn  # type: ignore

    template_id = uuid.uuid4()
    user_id = uuid.uuid4()

    asyncio.run(db.record_template_usage(user_id, template_id))

    assert any(
        "INSERT INTO template_usage" in call[1]
        for call in conn.calls
        if call[0] == "execute"
    )


def test_get_template_insights_builds_payload():
    db = Database()

    async def noop():
        return None

    db._ensure_template_usage_table = noop  # type: ignore

    conn = FakeConn()

    def get_conn():
        return ConnCtx(conn)

    db.get_connection = get_conn  # type: ignore

    result = asyncio.run(db.get_template_insights(uuid.uuid4()))

    assert result["counts"]["active"] == 3
    assert result["counts"]["usage_events"] == 5
    assert len(result["suggestions"]) == 1
    assert result["suggestions"][0]["match_score"] >= 40
    assert len(result["top_categories"]) == 2
    assert len(result["recent_templates"]) == 1


def test_delete_template_triggers_usage_cleanup():
    db = Database()

    async def noop(*args, **kwargs):
        return None

    called = {"cleanup": False}

    async def cleanup(template_id, user_id):
        called["cleanup"] = True

    db._cleanup_template_usage = cleanup  # type: ignore

    conn = FakeConn()
    conn.execute_result = "DELETE 1"

    def get_conn():
        return ConnCtx(conn)

    db.get_connection = get_conn  # type: ignore

    success = asyncio.run(db.delete_template(uuid.uuid4(), uuid.uuid4()))

    assert success is True
    assert called["cleanup"] is True


def test_generate_template_from_document_parses_json():
    ai = AIService()

    async def fake_generate_completion(*args, **kwargs):
        return AIResponse(
            content='{"title":"Arbeitsvertrag","category":"Arbeitsrecht","content":"<h1>Vertrag</h1><p>[Mandant] schließt...</p>","summary":"Kurzbeschreibung."}'
        )

    ai.generate_completion = fake_generate_completion  # type: ignore
    payload, response, meta = asyncio.run(ai.generate_template_from_document("Beispieltext für Vertrag", "Arbeitsvertrag.docx"))

    assert payload["title"] == "Arbeitsvertrag"
    assert "<h1>" in payload["content"]
    assert response.usage["import_chars"] > 0
    assert isinstance(meta["sanitized_text"], str)


def test_generate_template_from_document_raises_for_invalid_json():
    ai = AIService()

    async def fake_generate_completion(*args, **kwargs):
        return AIResponse(content="keine json antwort")

    ai.generate_completion = fake_generate_completion  # type: ignore
    with pytest.raises(ValueError):
        asyncio.run(ai.generate_template_from_document("Rechtsdokument", "Upload.pdf"))
