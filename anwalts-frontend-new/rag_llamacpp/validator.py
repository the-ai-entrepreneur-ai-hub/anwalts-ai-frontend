from __future__ import annotations

import json
import re
from typing import Dict, Any, List

from pydantic import BaseModel, Field, ValidationError


class OutputModel(BaseModel):
    laws: List[str]
    answer: str = Field(max_length=1200)
    examples: List[str] | None = None
    disclaimer: str


PATTERN_FAKE_BGH = re.compile(r"BGH,\s*1\s*StR\s*\d+", re.IGNORECASE)
PATTERN_FAKE_PAR = re.compile(r"§\s*\d+\s*Abs\.\s*\d+\s*Satz\s*\d+", re.IGNORECASE)


def preflight_rejects(text: str) -> bool:
    if PATTERN_FAKE_BGH.search(text):
        return True
    # Block clearly non-existent combinations like "Abs. 2 Satz 2" when law has no such sentence; here we only catch pattern risk.
    if PATTERN_FAKE_PAR.search(text):
        return True
    return False


def ensure_schema(text: str) -> OutputModel | None:
    try:
        data = json.loads(text)
        return OutputModel(**data)
    except (json.JSONDecodeError, ValidationError):
        return None
