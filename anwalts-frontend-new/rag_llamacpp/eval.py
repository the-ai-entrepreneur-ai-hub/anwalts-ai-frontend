from __future__ import annotations

import statistics
from typing import List, Dict, Any

from .assistant import GermanLawAssistant
from .utils import detect_statutes


EXPECTED = {
    "Voraussetzungen der Anfechtung (§ 119 BGB)": ["§ 119", "§ 121", "§ 142", "§ 122"],
    "Betrugstatbestand (§ 263 StGB)": ["§ 263"],
    "Fristlose Kündigung (§ 626 BGB)": ["§ 626"],
    "Jedermann-Festnahme (§ 127 Abs. 1 StPO)": ["§ 127"],
}


def evaluate(assistant: GermanLawAssistant, dataset: List[str]) -> Dict[str, Any]:
    latencies: List[int] = []
    correct_cites = 0
    hallucination_flags = 0
    word_counts: List[int] = []
    structure_ok = 0

    for q in dataset:
        out = assistant.ask(q)
        tel = out.get("telemetry", {})
        latencies.append(int(tel.get("latency_ms", 0)))

        laws = " ".join(out.get("laws", [])) + " " + out.get("answer", "")
        exp = EXPECTED.get(q, [])
        if all(any(e in laws for e in exp) for e in exp):
            correct_cites += 1

        if "Unzureichende Faktenlage" in out.get("answer", "") or not out.get("laws"):
            hallucination_flags += 0
        else:
            # crude heuristic: if cites a law not detected in query and not expected, flag potential hallucination
            detected = detect_statutes(q)
            cited = detect_statutes(laws)
            extra = [c for c in cited if not any(d in c for d in detected) and not any(e in c for e in exp)]
            if extra:
                hallucination_flags += 1

        word_counts.append(len(out.get("answer", "").split()))
        if isinstance(out.get("laws"), list) and isinstance(out.get("answer"), str) and isinstance(out.get("disclaimer"), str):
            structure_ok += 1

    return {
        "p50_latency_ms": int(statistics.median(sorted(latencies))) if latencies else 0,
        "p95_latency_ms": int(sorted(latencies)[int(0.95 * (len(latencies)-1))]) if latencies else 0,
        "correct_statute_citations": correct_cites,
        "hallucination_flags": hallucination_flags,
        "avg_word_count": float(sum(word_counts))/len(word_counts) if word_counts else 0.0,
        "structure_compliance": structure_ok,
    }
