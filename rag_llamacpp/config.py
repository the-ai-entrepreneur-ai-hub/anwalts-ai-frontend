from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional


@dataclass(frozen=True)
class SamplingConfig:
    temperature: float = 0.1
    top_p: float = 0.9
    top_k: int = 40
    min_p: float = 0.05
    repeat_penalty: float = 1.15
    max_tokens: int = 384
    stop: List[str] = field(default_factory=lambda: [
        "<|assistant|>",
        "Hinweis:",
        "Ende der Antwort.",
    ])


@dataclass(frozen=True)
class FastPath:
    max_tokens: int
    temperature: float


@dataclass(frozen=True)
class RuntimeConfig:
    engine: str
    model_file: str
    server_args: str
    sampling_defaults: SamplingConfig
    fast_paths: Dict[str, FastPath]


@dataclass(frozen=True)
class PromptingConfig:
    system_prompt: str
    guardrails: List[str]
    few_shots: List[Dict[str, str]]


@dataclass(frozen=True)
class VectorDBConfig:
    backend: str
    dsn: str
    table_docs: str
    table_chunks: str
    embedding_model: str
    top_k: int
    min_score: float
    freshness_bias_days: int
    path: Optional[str] = None


@dataclass(frozen=True)
class RetrievalConfig:
    enabled: bool
    policy: str
    vector_db: VectorDBConfig
    pre_query_hooks: List[str]
    post_merge_rules: List[str]


@dataclass(frozen=True)
class ServerSideBatching:
    parallel: int
    max_queue_delay_ms: int


@dataclass(frozen=True)
class CachingBatchingConfig:
    enable_prompt_cache: bool
    cache_ttl_seconds: int
    cache_key: str
    prefill_cache: List[str]
    server_side_batching: ServerSideBatching


@dataclass(frozen=True)
class OutputSchemaProperty:
    type: str
    items: Optional[Dict[str, Any]] = None
    maxLength: Optional[int] = None
    maxItems: Optional[int] = None


@dataclass(frozen=True)
class OutputSchema:
    type: str
    required: List[str]
    properties: Dict[str, OutputSchemaProperty]


@dataclass(frozen=True)
class ValidationConfig:
    preflight_checks: List[str]
    output_schema: OutputSchema


@dataclass(frozen=True)
class TelemetryAlert:
    when: str
    action: str


@dataclass(frozen=True)
class TelemetryConfig:
    log_usage: bool
    fields: List[str]
    store_in: str
    alerts: List[TelemetryAlert]


@dataclass(frozen=True)
class EvalLoopConfig:
    dataset: List[str]
    metrics: List[str]
    budget: Dict[str, int]


@dataclass(frozen=True)
class TuningPlan:
    step1_quant: str
    step2_prompt: str
    step3_sampling: str
    step4_ctx: str
    step5_rag: str
    step6_cache: str


@dataclass(frozen=True)
class RollbackPlan:
    on_latency_spike: List[str]
    on_hallucinations: List[str]


@dataclass(frozen=True)
class AppConfig:
    task: str
    targets: Dict[str, Any]
    runtime: RuntimeConfig
    prompting: PromptingConfig
    retrieval: RetrievalConfig
    caching_and_batching: CachingBatchingConfig
    validation: ValidationConfig
    telemetry: TelemetryConfig
    eval_loop: EvalLoopConfig
    tuning_plan: TuningPlan
    rollback: RollbackPlan
