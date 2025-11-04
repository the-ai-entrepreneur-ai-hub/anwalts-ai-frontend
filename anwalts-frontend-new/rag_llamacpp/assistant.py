from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Dict, Any, Optional, List

from .config import AppConfig, SamplingConfig
from .llama_client import LlamaClient
from .retrieval import VectorStore, LocalJsonStore, DummyEmbedder, filter_statute_snippets, merge_context
from .utils import PromptCache, detect_statutes, now_ms, apply_stop, to_json
from .validator import preflight_rejects, ensure_schema


@dataclass
class TelemetryRecord:
    latency_ms: int
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cache_hit: bool


class GermanLawAssistant:
    def __init__(self, cfg: AppConfig, host: str = "127.0.0.1", port: int = 8080) -> None:
        self.cfg = cfg
        self.client = LlamaClient(host=host, port=port)
        self.cache = PromptCache(ttl_seconds=cfg.caching_and_batching.cache_ttl_seconds)
        self.vector: Optional[VectorStore] = None
        self.embedder = DummyEmbedder()
        if self.cfg.retrieval.enabled:
            backend = cfg.retrieval.vector_db.backend.lower()
            if backend == "pgvector":
                self.vector = VectorStore(dsn=cfg.retrieval.vector_db.dsn, table_chunks=cfg.retrieval.vector_db.table_chunks)
            elif backend == "local_json" and cfg.retrieval.vector_db.path:
                self.vector = LocalJsonStore(path=cfg.retrieval.vector_db.path)

    def warm_cache(self) -> None:
        if not self.cfg.caching_and_batching.enable_prompt_cache:
            return
        # Best-effort warmup using common prompts; ignore results
        for q in self.cfg.caching_and_batching.prefill_cache:
            try:
                _ = self.ask(q)
            except Exception:
                continue

    def _choose_sampling(self, user_prompt: str) -> Dict[str, Any]:
        s = self.cfg.runtime.sampling_defaults
        sampling: Dict[str, Any] = dict(
            temperature=s.temperature,
            top_p=s.top_p,
            top_k=s.top_k,
            min_p=s.min_p,
            repeat_penalty=s.repeat_penalty,
            max_tokens=s.max_tokens,
            stop=s.stop,
        )
        low = user_prompt.lower()
        if len(user_prompt) < 120:
            fp = self.cfg.runtime.fast_paths.get("short_answers")
            if fp:
                sampling["max_tokens"] = min(sampling["max_tokens"], fp.max_tokens)
                sampling["temperature"] = min(sampling["temperature"], fp.temperature)
        if any(k in low for k in ["defini", "begriff", "was ist", "ist …"]):
            fp = self.cfg.runtime.fast_paths.get("definitions")
            if fp:
                sampling["max_tokens"] = min(sampling["max_tokens"], fp.max_tokens)
                sampling["temperature"] = min(sampling["temperature"], fp.temperature)
        if "§" in user_prompt:
            fp = self.cfg.runtime.fast_paths.get("statute_lookup")
            if fp:
                sampling["max_tokens"] = min(sampling["max_tokens"], fp.max_tokens)
                sampling["temperature"] = min(sampling["temperature"], fp.temperature)
        return sampling

    def _build_prompt(self, user_prompt: str, context: str) -> str:
        fs_examples = "\n\n".join(
            f"User: {e['user']}\nAssistant: {e['assistant']}" for e in self.cfg.prompting.few_shots
        )
        sys = self.cfg.prompting.system_prompt
        guard = "\n".join(f"- {g}" for g in self.cfg.prompting.guardrails)
        instruction = (
            "Formatiere die Ausgabe strikt als JSON passend zum Schema:\n"
            '{"laws":[], "answer":"...", "examples":["..."], "disclaimer":"..."}.\n'
            "Antworte auf Deutsch. Keine frei erfundenen Quellen."
        )
        rag_note = "Kontext (maßgeblich, wenn vorhanden):\n" + (context.strip() or "[kein RAG-Kontext]")
        return (
            f"System:\n{sys}\n\nGuardrails:\n{guard}\n\n{instruction}\n\n"
            f"{fs_examples}\n\n{rag_note}\n\nUser: {user_prompt}\nAssistant:"
        )

    def _maybe_retrieve(self, user_prompt: str) -> str:
        if not self.vector:
            return ""
        markers = detect_statutes(user_prompt)
        force = bool(markers)
        if self.cfg.retrieval.policy.lower().startswith("rag-first") or force:
            try:
                emb = self.embedder.embed(user_prompt)
                snippets = self.vector.query(emb, top_k=self.cfg.retrieval.vector_db.top_k,
                                             min_score=self.cfg.retrieval.vector_db.min_score)
                snippets = filter_statute_snippets(snippets, markers)
                return merge_context(snippets)
            except Exception:
                # Retrieval is best-effort; on any backend issue, fall back silently
                return ""
        return ""

    def ask(self, user_prompt: str) -> Dict[str, Any]:
        sampling = self._choose_sampling(user_prompt)
        cache_key = self.cache.make_key(self.cfg.prompting.system_prompt, user_prompt, sampling["top_p"], sampling["temperature"])
        cache_hit = False
        cached = self.cache.get(cache_key) if self.cfg.caching_and_batching.enable_prompt_cache else None
        if cached:
            cache_hit = True
            return cached

        context = self._maybe_retrieve(user_prompt)
        prompt = self._build_prompt(user_prompt, context)

        t0 = now_ms()
        resp = self.client.generate(prompt, sampling)
        latency_ms = now_ms() - t0

        raw_text = resp.text.strip().replace("\u0000", " ")
        # First try to parse JSON to avoid corrupting it with stop sequences
        model = ensure_schema(raw_text)
        if model is not None:
            combined_for_checks = " ".join(model.laws or []) + " " + (model.answer or "")
            if preflight_rejects(combined_for_checks):
                model_dict = {
                    "laws": [],
                    "answer": "Unzureichende Faktenlage – bitte präzisieren.",
                    "examples": [],
                    "disclaimer": "Hinweis: Keine Rechtsberatung.",
                }
            else:
                # Apply stop tokens only to the free-text answer field
                stopped_answer = apply_stop(model.answer, sampling.get("stop", []))
                model_dict = {
                    **model.model_dump(),
                    "answer": stopped_answer[:1150],
                    "disclaimer": model.disclaimer or "Hinweis: Keine Rechtsberatung.",
                }
        else:
            # Non-JSON output: apply stops to whole text, then wrap
            stopped = apply_stop(raw_text, sampling.get("stop", []))
            if preflight_rejects(stopped):
                stopped = "Unzureichende Faktenlage – bitte präzisieren."
            model_dict = {
                "laws": [],
                "answer": stopped[:1150],
                "examples": None,
                "disclaimer": "Hinweis: Keine Rechtsberatung.",
            }

        result = {
            **model_dict,
            "telemetry": {
                "latency_ms": latency_ms,
                "prompt_tokens": resp.prompt_tokens,
                "completion_tokens": resp.completion_tokens,
                "total_tokens": resp.total_tokens,
                "cache_hit": cache_hit,
            }
        }
        self.cache.set(cache_key, result)
        return result
