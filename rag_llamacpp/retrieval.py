from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple
import json
from pathlib import Path

import psycopg


@dataclass
class RetrievedChunk:
    text: str
    score: float
    meta: Dict[str, Any]


class VectorStore:
    def __init__(self, dsn: str, table_chunks: str) -> None:
        self.dsn = dsn
        self.table_chunks = table_chunks

    def query(self, query_embedding: List[float], top_k: int = 6, min_score: float = 0.35) -> List[RetrievedChunk]:
        with psycopg.connect(self.dsn) as conn:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    SELECT text, score, meta
                    FROM {self.table_chunks}
                    WHERE score >= %s
                    ORDER BY embedding <=> %s
                    LIMIT %s
                    """,
                    (min_score, query_embedding, top_k),
                )
                rows = cur.fetchall()
        return [RetrievedChunk(text=r[0], score=r[1], meta=r[2]) for r in rows]


class LocalJsonStore:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self._rows: List[RetrievedChunk] = []
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as f:
                for line in f:
                    obj = json.loads(line)
                    self._rows.append(
                        RetrievedChunk(text=obj["text"], score=float(obj.get("score", 1.0)), meta=obj.get("meta", {}))
                    )

    def query(self, query_embedding: List[float], top_k: int = 6, min_score: float = 0.0) -> List[RetrievedChunk]:
        # Simple lexical fallback: rank by overlap length between query hash and text length; deterministic for tests
        scored = []
        for r in self._rows:
            scored.append((len(r.text), r))
        scored.sort(key=lambda x: -x[0])
        return [r for _, r in scored[:top_k]]


class DummyEmbedder:
    def embed(self, text: str) -> List[float]:
        # Placeholder: deterministic hash-based pseudo-embedding for testing
        import hashlib
        h = hashlib.sha256(text.encode("utf-8")).digest()
        # Convert first 32 bytes to 8 floats
        return [int.from_bytes(h[i:i+4], 'big') / 2**32 for i in range(0, 32, 4)]


def filter_statute_snippets(snippets: List[RetrievedChunk], statute_markers: List[str]) -> List[RetrievedChunk]:
    if not statute_markers:
        return snippets
    lower_markers = [m.lower() for m in statute_markers]
    filtered: List[RetrievedChunk] = []
    for s in snippets:
        mtext = s.meta.get("law_ref", "").lower() if isinstance(s.meta, dict) else ""
        if any(m in mtext for m in lower_markers):
            filtered.append(s)
    return filtered or snippets


def merge_context(snippets: List[RetrievedChunk], max_chars: int = 2200) -> str:
    buf: List[str] = []
    total = 0
    for s in snippets:
        t = s.text.strip()
        if not t:
            continue
        if total + len(t) + 2 > max_chars:
            break
        buf.append(t)
        total += len(t) + 2
    return "\n\n".join(buf)
