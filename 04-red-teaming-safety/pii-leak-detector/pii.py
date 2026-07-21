"""Detect and redact personally identifiable information (PII) in text.

Model outputs and training data can leak PII — emails, phone numbers, credit cards,
SSNs, IP addresses. This module finds those spans with transparent patterns (and a
Luhn check for card numbers to cut false positives), reports what was found, and can
redact it. It's a defensive utility for scrubbing datasets and screening outputs,
scored on a labeled set.
"""
from __future__ import annotations

import re

PATTERNS: dict[str, str] = {
    "email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "phone": r"(?<!\d)(?:\+?1[-.\s]?)?(?:\(\d{3}\)|\d{3})[-.\s]?\d{3}[-.\s]?\d{4}(?!\d)",
    "ssn": r"(?<!\d)\d{3}-\d{2}-\d{4}(?!\d)",
    "credit_card": r"(?<!\d)(?:\d[ -]?){13,16}(?!\d)",
    "ipv4": r"(?<!\d)(?:\d{1,3}\.){3}\d{1,3}(?!\d)",
}

_COMPILED = {name: re.compile(p) for name, p in PATTERNS.items()}


def _luhn_ok(digits: str) -> bool:
    """Luhn checksum used to validate credit-card numbers and reject random digits."""
    nums = [int(c) for c in digits if c.isdigit()]
    if len(nums) < 13:
        return False
    total, parity = 0, len(nums) % 2
    for i, n in enumerate(nums):
        if i % 2 == parity:
            n *= 2
            if n > 9:
                n -= 9
        total += n
    return total % 10 == 0


def _valid_ipv4(text: str) -> bool:
    return all(0 <= int(o) <= 255 for o in text.split("."))


def find_pii(text: str) -> list[dict]:
    """Return found PII spans: {type, value, start, end}, sorted by position."""
    found: list[dict] = []
    for name, rx in _COMPILED.items():
        for m in rx.finditer(text):
            value = m.group()
            if name == "credit_card" and not _luhn_ok(value):
                continue
            if name == "ipv4" and not _valid_ipv4(value):
                continue
            found.append({"type": name, "value": value, "start": m.start(), "end": m.end()})
    # de-overlap: prefer the earliest, longest match when spans collide
    found.sort(key=lambda d: (d["start"], -(d["end"] - d["start"])))
    result, last_end = [], -1
    for span in found:
        if span["start"] >= last_end:
            result.append(span)
            last_end = span["end"]
    return result


def redact(text: str, mask: str = "[REDACTED]") -> str:
    spans = find_pii(text)
    out, cursor = [], 0
    for s in spans:
        out.append(text[cursor : s["start"]])
        out.append(mask)
        cursor = s["end"]
    out.append(text[cursor:])
    return "".join(out)


def evaluate(dataset: list[dict]) -> dict:
    """Score detection on rows: {text, has_pii: bool}. Flagged == any PII found."""
    tp = fp = tn = fn = 0
    for row in dataset:
        flagged = bool(find_pii(row["text"]))
        actual = row["has_pii"]
        if flagged and actual:
            tp += 1
        elif flagged and not actual:
            fp += 1
        elif not flagged and actual:
            fn += 1
        else:
            tn += 1
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {
        "n": len(dataset),
        "confusion": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }
