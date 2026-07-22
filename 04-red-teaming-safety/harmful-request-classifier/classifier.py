"""Tiered risk classifier for user requests (a safety-routing aid, not a model gate).

A safety layer often needs a fast first-pass triage of incoming requests into risk
tiers: clearly benign ("allow"), sensitive-but-answerable ("caution", e.g. medical or
legal questions that need care and disclaimers), and disallowed ("refuse"). This is a
transparent, rule-based classifier for that triage, scored against a labeled set. It is
deliberately conservative and interpretable; a production system would layer a model
classifier on top, but the tiers and the evaluation methodology are the point.
"""
from __future__ import annotations

import re

# Highest tier wins: refuse > caution > allow.
_REFUSE = [
    r"\bhow to (make|build|synthesi[sz]e)\b.*\b(bomb|explosive|weapon|meth|nerve agent)\b",
    r"\b(hack|break) into\b.*\b(account|bank|network|system)\b",
    r"\bhurt (myself|yourself)\b|\bkill (myself|someone)\b",
    r"\bmalware\b|\bransomware\b|\bkeylogger\b",
    r"\bcredit card numbers?\b.*\b(steal|dump|generate)\b|\b(steal|dump|generate)\b.*\bcredit card numbers?\b",
    r"\bevade (police|taxes)\b|\blaunder money\b",
]
_CAUTION = [
    r"\b(symptom|diagnos|dosage|medication|prescription)\b",
    r"\b(lawsuit|legal advice|sue|custody|tax)\b",
    r"\b(invest|stocks?|crypto|portfolio)\b.*\b(should i|advice|recommend)\b",
    r"\bmental health\b|\banxiety\b|\bdepress",
]

_REFUSE_RX = [re.compile(p, re.IGNORECASE) for p in _REFUSE]
_CAUTION_RX = [re.compile(p, re.IGNORECASE) for p in _CAUTION]


def classify(text: str) -> dict:
    """Return {tier, reason}. tier in {refuse, caution, allow}."""
    for rx in _REFUSE_RX:
        if rx.search(text):
            return {"tier": "refuse", "reason": rx.pattern}
    for rx in _CAUTION_RX:
        if rx.search(text):
            return {"tier": "caution", "reason": rx.pattern}
    return {"tier": "allow", "reason": "no risk pattern matched"}


def evaluate(dataset: list[dict]) -> dict:
    """Score tier prediction against labeled rows: {text, tier}."""
    tiers = ["allow", "caution", "refuse"]
    n = len(dataset)
    correct = 0
    # confusion as actual -> predicted counts
    confusion = {a: {p: 0 for p in tiers} for a in tiers}
    for row in dataset:
        pred = classify(row["text"])["tier"]
        actual = row["tier"]
        confusion[actual][pred] += 1
        if pred == actual:
            correct += 1
    # per-tier recall (of the actual X, how many predicted X)
    recall = {}
    for a in tiers:
        total = sum(confusion[a].values())
        recall[a] = round(confusion[a][a] / total, 4) if total else None
    return {
        "n": n,
        "accuracy": round(correct / n, 4) if n else 0.0,
        "per_tier_recall": recall,
        "confusion": confusion,
    }
