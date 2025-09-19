from __future__ import annotations

import json
import os
from typing import Any

from rag_llamacpp.config_loader import load_config_from_json_str
from rag_llamacpp.assistant import GermanLawAssistant
from rag_llamacpp.eval import evaluate


CONFIG_JSON = r"""
REPLACED_AT_RUNTIME
"""


def main() -> None:
    cfg_json = os.environ.get("LAW_ASSISTANT_CONFIG_JSON")
    if not cfg_json:
        raise SystemExit("Set LAW_ASSISTANT_CONFIG_JSON to the provided JSON config string.")

    cfg = load_config_from_json_str(cfg_json)
    host = "127.0.0.1"
    port = 8080
    assistant = GermanLawAssistant(cfg, host=host, port=port)

    metrics = evaluate(assistant, cfg.eval_loop.dataset)
    print(json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
