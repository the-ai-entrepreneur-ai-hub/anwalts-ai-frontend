from __future__ import annotations

import hashlib
import json
import re
import time
from typing import Dict, Any, List, Optional, Tuple

import orjson
from cachetools import TTLCache


SECTION_PATTERN = re.compile(r"(§\s*\d+[a-z]*\s*(?:Abs\.|Satz|Nr\.)?\s*\d*)", flags=re.IGNORECASE)


class PromptCache:
    def __init__(self, ttl_seconds: int, maxsize: int = 4096) -> None:
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl_seconds)

    @staticmethod
    def _hash_key(system_prompt: str, user_prompt: str, top_p: float, temperature: float) -> str:
        normalized = f"{system_prompt}\n\n{user_prompt.strip()}|{top_p}|{temperature}".encode("utf-8")
        return hashlib.sha256(normalized).hexdigest()

    def make_key(self, system_prompt: str, user_prompt: str, top_p: float, temperature: float) -> str:
        return self._hash_key(system_prompt, user_prompt, top_p, temperature)

    def get(self, key: str) -> Optional[Dict[str, Any]]:
        return self.cache.get(key)

    def set(self, key: str, value: Dict[str, Any]) -> None:
        self.cache[key] = value


def detect_statutes(query: str) -> List[str]:
    return list({m.group(1).strip() for m in SECTION_PATTERN.finditer(query)})


def now_ms() -> int:
    return int(time.time() * 1000)


def apply_stop(text: str, stops: List[str]) -> str:
    for s in stops:
        if not s:
            continue
        idx = text.find(s)
        if idx != -1:
            text = text[:idx]
    return text


class JsonSafeEncoder(json.JSONEncoder):
    def default(self, obj):  # type: ignore[override]
        try:
            return super().default(obj)
        except TypeError:
            return str(obj)


def to_json(data: Dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, separators=(",", ":"), cls=JsonSafeEncoder)


def to_orjson(data: Dict[str, Any]) -> bytes:
    return orjson.dumps(data, option=orjson.OPT_NON_STR_KEYS)
