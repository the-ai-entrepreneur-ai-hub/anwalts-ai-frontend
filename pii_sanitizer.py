import re
from typing import Dict, Tuple

_PATTERNS = [
    (re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE), "[REDACTED_EMAIL]"),
    (re.compile(r"\b(?:[A-Z]{2}\d{2})(?:\s?[0-9A-Z]{4}){2,5}\b", re.IGNORECASE), "[REDACTED_IBAN]"),
    (re.compile(r"\b(?:\+?\d{1,3}[\s./-]?)?(?:\(?\d{2,4}\)?[\s./-]?)?\d{3,4}[\s./-]?\d{3,4}\b"), "[REDACTED_PHONE]"),
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "[REDACTED_IP]"),
    (re.compile(r"\b[A-ZÄÖÜ][\wäöüß.-]*?(?:straße|strasse|weg|platz|gasse|allee)\s+\d+[a-zA-Z]?\b", re.IGNORECASE), "[REDACTED_ADDRESS]"),
    (re.compile(r"\b(?:Geburtsdatum|Geboren am)\s*\d{2}\.\d{2}\.\d{4}\b", re.IGNORECASE), "[REDACTED_DOB]"),
    (re.compile(r"\b\d{5}(?:[-\s]?\d{4})?\b"), "[REDACTED_POSTAL]"),
]

_NAME_PATTERN = re.compile(
    r"\b(?:Herr|Frau|Dr\.?|RA|Rechtsanwalt|Rechtsanwältin)?\s*[A-ZÄÖÜ][a-zäöüß]+(?:\s+[A-ZÄÖÜ][a-zäöüß]+)+\b"
)


def sanitize_text(text: str) -> Tuple[str, Dict[str, int]]:
    """
    Perform lightweight PII scrubbing on user-provided text.
    Returns the redacted text and a dict describing replacement counts.
    """
    if not text:
        return "", {}

    replacements: Dict[str, int] = {}
    scrubbed = text

    for pattern, token in _PATTERNS:
        scrubbed, count = pattern.subn(token, scrubbed)
        if count:
            replacements[token] = replacements.get(token, 0) + count

    def _name_replacer(match: re.Match) -> str:
        replacements["[REDACTED_PERSON]"] = replacements.get("[REDACTED_PERSON]", 0) + 1
        return "[REDACTED_PERSON]"

    scrubbed = _NAME_PATTERN.sub(_name_replacer, scrubbed)

    scrubbed = re.sub(r"[ \t]+\n", "\n", scrubbed)
    scrubbed = re.sub(r"\n{3,}", "\n\n", scrubbed).strip()

    return scrubbed, replacements
