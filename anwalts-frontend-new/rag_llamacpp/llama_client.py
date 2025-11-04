from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests
from tenacity import retry, wait_exponential_jitter, stop_after_attempt, retry_if_exception_type


@dataclass
class LlamaResponse:
    text: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    model_latency_ms: int


class LlamaServerError(Exception):
    pass


class LlamaClient:
    def __init__(self, host: str = "127.0.0.1", port: int = 8080, timeout_s: int = 25) -> None:
        self.base_url = f"http://{host}:{port}"
        self.timeout_s = timeout_s

    @retry(wait=wait_exponential_jitter(initial=0.25, max=2.0), stop=stop_after_attempt(3),
           retry=retry_if_exception_type((requests.RequestException, LlamaServerError)))
    def generate(self, prompt: str, sampling: Dict[str, Any]) -> LlamaResponse:
        url = f"{self.base_url}/completion"
        payload = {
            "prompt": prompt,
            "temperature": sampling.get("temperature", 0.1),
            "top_p": sampling.get("top_p", 0.9),
            "top_k": sampling.get("top_k", 40),
            "min_p": sampling.get("min_p", 0.05),
            "repeat_penalty": sampling.get("repeat_penalty", 1.15),
            "n_predict": sampling.get("max_tokens", 384),
            "stop": sampling.get("stop", []),
            "cache_prompt": True,
            "stream": False,
        }
        r = requests.post(url, json=payload, timeout=self.timeout_s)
        if r.status_code != 200:
            raise LlamaServerError(f"Status {r.status_code}: {r.text}")
        data = r.json()
        return LlamaResponse(
            text=data.get("content", ""),
            prompt_tokens=data.get("tokens_evaluated", 0),
            completion_tokens=data.get("tokens_predicted", 0),
            total_tokens=data.get("tokens_evaluated", 0) + data.get("tokens_predicted", 0),
            model_latency_ms=int(data.get("timings", {}).get("predicted_ms", 0)),
        )
