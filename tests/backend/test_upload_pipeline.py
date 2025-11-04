import asyncio
import importlib
import sys

import pytest


class DummyFile:
    def __init__(self, data: bytes, filename: str = "test.txt", content_type: str = "text/plain"):
        self._data = data
        self.filename = filename
        self.content_type = content_type

    async def read(self) -> bytes:  # pragma: no cover - exercised in tests
        return self._data


def _reload_upload_processor(tmp_path, monkeypatch):
    monkeypatch.setenv("UPLOAD_ROOT", str(tmp_path))
    if "upload_processor" in sys.modules:
        module = importlib.reload(sys.modules["upload_processor"])
    else:
        module = importlib.import_module("upload_processor")
    return module


def test_process_existing_reuses_cached_sanitized(tmp_path, monkeypatch):
    upload_processor = _reload_upload_processor(tmp_path, monkeypatch)

    sample_text = (
        "Herr Max Mustermann wohnt in Teststraße 5, 12345 Berlin.\n"
        "Geburtsdatum 12.05.1985\n"
        "IBAN DE89 3704 0044 0532 0130 00\n"
        "Telefon +49 30 1234567\n"
        "Email max@example.com"
    ).encode("utf-8")

    result = asyncio.run(upload_processor.handle_upload(DummyFile(sample_text), "user-1"))
    file_id = result["file_id"]

    content = upload_processor.get_file_content(file_id)
    assert content is not None
    assert "[REDACTED_EMAIL]" in content
    assert "[REDACTED_IBAN]" in content
    assert "[REDACTED_ADDRESS]" in content
    assert "[REDACTED_DOB]" in content

    def _fail_sanitize(*_args, **_kwargs):
        pytest.fail("sanitize_text should not run when sanitized content exists")

    monkeypatch.setattr(upload_processor, "sanitize_text", _fail_sanitize)

    processed = asyncio.run(upload_processor.process_existing(file_id))
    assert processed["success"] is True
    assert processed["content_preview"]
    assert "[REDACTED_EMAIL]" in processed["content_preview"]


def test_process_existing_resanitizes_when_missing(tmp_path, monkeypatch):
    upload_processor = _reload_upload_processor(tmp_path, monkeypatch)

    plain_text = b"Unkritischer Text"
    result = asyncio.run(upload_processor.handle_upload(DummyFile(plain_text), "user-2"))
    file_id = result["file_id"]

    sanitized_path = upload_processor._content_path(file_id)  # type: ignore[attr-defined]
    if sanitized_path.exists():
        sanitized_path.unlink()

    call_counter = {"count": 0}

    def _stub_sanitize(text):
        call_counter["count"] += 1
        return ("SANITIZED TEXT", {"[MASKED]": 1})

    monkeypatch.setattr(upload_processor, "sanitize_text", _stub_sanitize)

    processed = asyncio.run(upload_processor.process_existing(file_id))
    assert call_counter["count"] == 1
    assert processed["content_preview"].startswith("SANITIZED TEXT")

    regenerated = upload_processor.get_file_content(file_id)
    assert regenerated == "SANITIZED TEXT"
