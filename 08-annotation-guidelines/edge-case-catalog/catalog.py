"""Edge-case detection for a sentiment-annotation task.

The hardest part of a labeling task is the edge cases, and a good guideline names them
and tells annotators how to handle them. This module encodes the catalog in
EDGE_CASES.md as detectors: given a piece of text it flags which tricky patterns apply
(negation, contrast/mixed, sarcasm cue, comparison, rhetorical question, conditional)
so the annotation tool can surface the right rule. It routes attention; it does not
assign the final sentiment label.
"""
from __future__ import annotations

import re

# Each edge case: a rule id -> compiled detectors. Matching any pattern flags the case.
_PATTERNS: dict[str, list[str]] = {
    "negation": [r"\bnot\b", r"\bnever\b", r"\bno longer\b", r"\bdidn'?t\b", r"\bwasn'?t\b", r"\bisn'?t\b"],
    "contrast_mixed": [r"\bbut\b", r"\bhowever\b", r"\balthough\b", r"\bthough\b", r"\bon the other hand\b"],
    "sarcasm_cue": [r"\byeah right\b", r"\boh great\b", r"\bjust what i needed\b", r'"[^"]+"', r"\bsure+\b.*\?"],
    "comparison": [r"\bbetter than\b", r"\bworse than\b", r"\bcompared to\b", r"\bmore .* than\b", r"\bless .* than\b"],
    "rhetorical_question": [r"\?\s*$"],
    "conditional": [r"\bif\b.*\bwould\b", r"\bwould have\b", r"\bunless\b"],
}

_COMPILED = {rule: [re.compile(p, re.IGNORECASE) for p in pats] for rule, pats in _PATTERNS.items()}


def detect_edge_cases(text: str) -> list[str]:
    """Return the sorted list of edge-case rule ids that apply to the text."""
    hits = [rule for rule, rxs in _COMPILED.items() if any(rx.search(text) for rx in rxs)]
    return sorted(hits)


def needs_careful_review(text: str) -> bool:
    """True if any edge case applies — the annotation tool should show the guideline."""
    return bool(detect_edge_cases(text))


def route(dataset: list[dict]) -> dict:
    """Tally which edge cases appear across a dataset of {id, text} rows."""
    counts: dict[str, int] = {}
    flagged = 0
    per_item = []
    for row in dataset:
        cases = detect_edge_cases(row["text"])
        if cases:
            flagged += 1
        for c in cases:
            counts[c] = counts.get(c, 0) + 1
        per_item.append({"id": row.get("id"), "edge_cases": cases})
    n = len(dataset)
    return {
        "n": n,
        "flagged_for_review": flagged,
        "flag_rate": round(flagged / n, 4) if n else 0.0,
        "counts_by_case": dict(sorted(counts.items())),
        "per_item": per_item,
    }
