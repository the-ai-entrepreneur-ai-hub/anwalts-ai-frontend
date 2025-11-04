import asyncio
import json
import mimetypes
import os
import shutil
import uuid
import logging
import time
from collections import OrderedDict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from pii_sanitizer import sanitize_text

try:
    from pypdf import PdfReader  # type: ignore
except Exception:  # pragma: no cover
    PdfReader = None

try:
    import docx  # type: ignore
except Exception:  # pragma: no cover
    docx = None


UPLOAD_ROOT = Path(os.getenv("UPLOAD_ROOT", "/app/uploads")).resolve()
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_BYTES", 10 * 1024 * 1024))

logger = logging.getLogger(__name__)
_MAX_CACHE_ITEMS = max(int(os.getenv("UPLOAD_SANITIZED_CACHE_SIZE", "32")), 0)
_SANITIZED_CACHE: "OrderedDict[str, str]" = OrderedDict()


def _safe_filename(name: str) -> str:
    candidate = Path(name).name or "upload"
    safe = "".join(ch for ch in candidate if ch.isalnum() or ch in ("-", "_", ".", " "))
    return safe.replace(" ", "_") or f"upload_{uuid.uuid4().hex}"


def _folder(file_id: str) -> Path:
    return UPLOAD_ROOT / file_id


def _meta_path(file_id: str) -> Path:
    return _folder(file_id) / "meta.json"


def _content_path(file_id: str) -> Path:
    return _folder(file_id) / "content.txt"


def _original_path(file_id: str) -> Path:
    return _folder(file_id) / "original"


def _cache_get(file_id: str) -> Optional[str]:
    if _MAX_CACHE_ITEMS <= 0:
        return None
    text = _SANITIZED_CACHE.get(file_id)
    if text is not None:
        _SANITIZED_CACHE.move_to_end(file_id)
    return text


def _cache_put(file_id: str, content: str) -> None:
    if _MAX_CACHE_ITEMS <= 0:
        return
    _SANITIZED_CACHE[file_id] = content
    _SANITIZED_CACHE.move_to_end(file_id)
    while len(_SANITIZED_CACHE) > _MAX_CACHE_ITEMS:
        _SANITIZED_CACHE.popitem(last=False)


def _cache_remove(file_id: str) -> None:
    if _MAX_CACHE_ITEMS <= 0:
        return
    _SANITIZED_CACHE.pop(file_id, None)


def _write_meta(file_id: str, meta: Dict[str, Any]) -> None:
    path = _meta_path(file_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")


def _load_meta(file_id: str) -> Optional[Dict[str, Any]]:
    path = _meta_path(file_id)
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _build_preview(text: str) -> str:
    preview = text[:600]
    if len(text) > 600:
        preview += "…"
    return preview


def _persist_sanitized_payload(
    file_id: str,
    meta: Dict[str, Any],
    sanitized_text: str,
    replacements: Dict[str, int],
    *,
    processing_time_ms: Optional[int] = None,
) -> Dict[str, Any]:
    _content_path(file_id).write_text(sanitized_text, encoding="utf-8")
    _cache_put(file_id, sanitized_text)

    processed_meta = dict(meta)
    processed_meta.update(
        {
            "replacements": replacements,
            "processed_at": datetime.utcnow().isoformat() + "Z",
            "has_text": bool(sanitized_text.strip()),
            "sanitized_preview": _build_preview(sanitized_text),
            "sanitized_word_count": len(sanitized_text.split()),
        }
    )
    if processing_time_ms is not None:
        processed_meta["processing_time_ms"] = processing_time_ms

    _write_meta(file_id, processed_meta)
    return processed_meta


def _extract_text(file_path: Path, content_type: str) -> str:
    suffix = file_path.suffix.lower()
    if suffix == ".txt" or content_type.startswith("text/"):
        return file_path.read_text(encoding="utf-8", errors="ignore")

    if suffix == ".pdf":
        if PdfReader is None:
            return ""
        try:
            reader = PdfReader(str(file_path))
            pages = []
            for page in reader.pages:
                try:
                    pages.append(page.extract_text() or "")
                except Exception:
                    continue
            return "\n".join(pages)
        except Exception:
            return ""

    if suffix == ".docx":
        if docx is None:
            return ""
        try:
            document = docx.Document(str(file_path))
            return "\n".join(p.text for p in document.paragraphs)
        except Exception:
            return ""

    return file_path.read_bytes().decode("utf-8", errors="ignore")


async def handle_upload(file, user_id: str, db=None) -> Dict[str, Any]:  # noqa: ANN001
    """
    Persist uploaded file, extract text, and return sanitized metadata.
    Designed to be called from FastAPI endpoints.
    """
    file_id = uuid.uuid4().hex
    folder = _folder(file_id)
    folder.mkdir(parents=True, exist_ok=True)

    original_name = getattr(file, "filename", None) or "upload"
    safe_name = _safe_filename(original_name)
    content_type = getattr(file, "content_type", None) or mimetypes.guess_type(original_name)[0] or "application/octet-stream"

    read_start = time.perf_counter()
    raw_bytes = await file.read()  # type: ignore[attr-defined]
    if len(raw_bytes) > MAX_UPLOAD_SIZE:
        raise ValueError("File exceeds maximum allowed size (10 MB)")

    original_path = _original_path(file_id)
    original_path.write_bytes(raw_bytes)

    stored_path = folder / safe_name
    stored_path.write_bytes(raw_bytes)

    loop = asyncio.get_running_loop()
    extracted_text = await loop.run_in_executor(None, _extract_text, stored_path, content_type)
    sanitize_start = time.perf_counter()
    sanitized_text, replacements = sanitize_text(extracted_text)
    sanitize_elapsed_ms = int((time.perf_counter() - sanitize_start) * 1000)
    total_elapsed_ms = int((time.perf_counter() - read_start) * 1000)

    if sanitize_elapsed_ms > 300:
        logger.warning(
            "Upload %s sanitization slow: %dms (total=%dms size=%d bytes, type=%s)",
            file_id,
            sanitize_elapsed_ms,
            total_elapsed_ms,
            len(raw_bytes),
            content_type,
        )

    meta = {
        "file_id": file_id,
        "user_id": str(user_id),
        "filename": safe_name,
        "original_filename": original_name,
        "content_type": content_type,
        "size_bytes": len(raw_bytes),
        "uploaded_at": datetime.utcnow().isoformat() + "Z",
        "has_text": bool(sanitized_text.strip()),
        "replacements": replacements,
        "processing_time_ms": sanitize_elapsed_ms,
    }
    processed_meta = _persist_sanitized_payload(
        file_id,
        meta,
        sanitized_text,
        replacements,
        processing_time_ms=sanitize_elapsed_ms,
    )
    preview = processed_meta.get("sanitized_preview", _build_preview(sanitized_text))
    word_count = processed_meta.get("sanitized_word_count", len(sanitized_text.split()))

    return {
        **processed_meta,
        "success": True,
        "content_preview": preview,
        "word_count": word_count,
    }


def list_user_files(user_id: str) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for folder in UPLOAD_ROOT.glob("*"):
        meta = _load_meta(folder.name)
        if meta and str(meta.get("user_id")) == str(user_id):
            items.append(meta)
    items.sort(key=lambda item: item.get("uploaded_at", ""), reverse=True)
    return items


def get_file_content(file_id: str) -> Optional[str]:
    cached = _cache_get(file_id)
    if cached is not None:
        return cached

    path = _content_path(file_id)
    if path.exists():
        try:
            text = path.read_text(encoding="utf-8")
            _cache_put(file_id, text)
            return text
        except Exception as exc:
            logger.warning("Failed to read sanitized content for %s: %s", file_id, exc)

    meta = _load_meta(file_id)
    if not meta:
        return None

    stored_path = _folder(file_id) / (meta.get("filename") or "")
    if not stored_path.exists():
        stored_path = _original_path(file_id)
    if not stored_path.exists():
        return None

    try:
        extracted_text = _extract_text(stored_path, meta.get("content_type", "application/octet-stream"))
        sanitized_text, replacements = sanitize_text(extracted_text)
        _persist_sanitized_payload(
            file_id,
            meta,
            sanitized_text,
            replacements,
        )
        logger.info("Regenerated sanitized content for %s after cache miss", file_id)
        return sanitized_text
    except Exception as exc:
        logger.error("Failed to regenerate sanitized content for %s: %s", file_id, exc)
        return None


def get_file_metadata(file_id: str) -> Optional[Dict[str, Any]]:
    return _load_meta(file_id)


def delete_file(file_id: str) -> bool:
    folder = _folder(file_id)
    if not folder.exists():
        return False
    try:
        shutil.rmtree(folder)
        _cache_remove(file_id)
        return True
    except Exception as exc:
        logger.error("Failed to delete upload %s: %s", file_id, exc)
        return False


async def process_existing(file_id: str, db=None) -> Dict[str, Any]:
    meta = _load_meta(file_id)
    if not meta:
        raise FileNotFoundError("File metadata missing")

    cached = _cache_get(file_id)
    if cached is None:
        content_path = _content_path(file_id)
        if content_path.exists():
            try:
                cached = content_path.read_text(encoding="utf-8")
                _cache_put(file_id, cached)
            except Exception as exc:
                logger.warning("Failed to read cached sanitized content for %s: %s", file_id, exc)

    if cached is not None and meta.get("processed_at"):
        preview = meta.get("sanitized_preview") or _build_preview(cached)
        word_count = meta.get("sanitized_word_count") or len(cached.split())
        return {
            **meta,
            "success": True,
            "content_preview": preview,
            "word_count": word_count,
        }

    stored_path = _folder(file_id) / (meta.get("filename") or "")
    if not stored_path.exists():
        stored_path = _original_path(file_id)
    if not stored_path.exists():
        raise FileNotFoundError("Original upload missing on disk")

    content_type = meta.get(
        "content_type",
        mimetypes.guess_type(meta.get("filename", ""))[0] or "application/octet-stream",
    )
    loop = asyncio.get_running_loop()
    sanitize_start = time.perf_counter()
    extracted_text = await loop.run_in_executor(None, _extract_text, stored_path, content_type)
    sanitized_text, replacements = sanitize_text(extracted_text)
    sanitize_elapsed_ms = int((time.perf_counter() - sanitize_start) * 1000)

    if sanitize_elapsed_ms > 300:
        logger.warning(
            "Reprocess of upload %s took %dms (type=%s)",
            file_id,
            sanitize_elapsed_ms,
            content_type,
        )

    processed_meta = _persist_sanitized_payload(
        file_id,
        meta,
        sanitized_text,
        replacements,
        processing_time_ms=sanitize_elapsed_ms,
    )
    preview = processed_meta.get("sanitized_preview", _build_preview(sanitized_text))
    word_count = processed_meta.get("sanitized_word_count", len(sanitized_text.split()))

    return {
        **processed_meta,
        "success": True,
        "content_preview": preview,
        "word_count": word_count,
    }
