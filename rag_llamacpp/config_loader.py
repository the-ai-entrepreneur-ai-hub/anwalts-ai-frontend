from __future__ import annotations

import json
from typing import Any, Dict

from .config import (
    AppConfig, RuntimeConfig, SamplingConfig, FastPath, PromptingConfig, RetrievalConfig,
    VectorDBConfig, CachingBatchingConfig, ServerSideBatching, ValidationConfig, OutputSchema,
    OutputSchemaProperty, TelemetryConfig, TelemetryAlert, EvalLoopConfig, TuningPlan, RollbackPlan,
)


def _map_output_schema(d: Dict[str, Any]) -> OutputSchema:
    props = {k: OutputSchemaProperty(**v) for k, v in d["properties"].items()}
    return OutputSchema(type=d["type"], required=d["required"], properties=props)


def load_config_from_json_str(s: str) -> AppConfig:
    j = json.loads(s)
    runtime = j["runtime"]
    sampling = SamplingConfig(**runtime["sampling_defaults"])  # type: ignore[arg-type]
    fast_paths = {k: FastPath(**v) for k, v in runtime.get("fast_paths", {}).items()}
    runtime_cfg = RuntimeConfig(engine=runtime["engine"], model_file=runtime["model_file"],
                                server_args=runtime["server_args"], sampling_defaults=sampling, fast_paths=fast_paths)

    prompting = j["prompting"]
    prompting_cfg = PromptingConfig(system_prompt=prompting["system_prompt"], guardrails=prompting["guardrails"],
                                    few_shots=prompting["few_shots"])

    retrieval = j["retrieval"]
    vcfg = retrieval["vector_db"]
    vector_db_cfg = VectorDBConfig(**vcfg)
    retrieval_cfg = RetrievalConfig(enabled=retrieval["enabled"], policy=retrieval["policy"],
                                    vector_db=vector_db_cfg, pre_query_hooks=retrieval["pre_query_hooks"],
                                    post_merge_rules=retrieval["post_merge_rules"])

    cb = j["caching_and_batching"]
    ssb = ServerSideBatching(**cb["server_side_batching"])  # type: ignore[arg-type]
    caching_cfg = CachingBatchingConfig(enable_prompt_cache=cb["enable_prompt_cache"], cache_ttl_seconds=cb["cache_ttl_seconds"],
                                        cache_key=cb["cache_key"], prefill_cache=cb["prefill_cache"],
                                        server_side_batching=ssb)

    val = j["validation"]
    output_schema = _map_output_schema(val["output_schema"])  # type: ignore[arg-type]
    validation_cfg = ValidationConfig(preflight_checks=val["preflight_checks"], output_schema=output_schema)

    tel = j["telemetry"]
    alerts = [TelemetryAlert(**a) for a in tel.get("alerts", [])]
    telemetry_cfg = TelemetryConfig(log_usage=tel["log_usage"], fields=tel["fields"], store_in=tel["store_in"], alerts=alerts)

    eval_loop = j["eval_loop"]
    eval_cfg = EvalLoopConfig(dataset=eval_loop["dataset"], metrics=eval_loop["metrics"], budget=eval_loop["budget"])  # type: ignore[arg-type]

    tune = j["tuning_plan"]
    tuning_cfg = TuningPlan(**tune)

    rb = j["rollback"]
    rollback_cfg = RollbackPlan(on_latency_spike=rb["on_latency_spike"], on_hallucinations=rb["on_hallucinations"])  # type: ignore[arg-type]

    return AppConfig(task=j["task"], targets=j["targets"], runtime=runtime_cfg, prompting=prompting_cfg,
                     retrieval=retrieval_cfg, caching_and_batching=caching_cfg, validation=validation_cfg,
                     telemetry=telemetry_cfg, eval_loop=eval_cfg, tuning_plan=tuning_cfg, rollback=rollback_cfg)
