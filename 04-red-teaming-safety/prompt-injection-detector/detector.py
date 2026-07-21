"""A defensive prompt-injection detector and its evaluation.

Tool-using agents read untrusted content (web pages, documents, tool output) that
may contain instructions aimed at hijacking the agent — "ignore previous
instructions", data-exfiltration requests, role spoofing, destructive commands.
This module flags that content with a transparent, rule-based detector and scores
the detector against a labeled dataset (precision / recall / F1 / accuracy).

The goal is detection, not attack: the signals are recognizable patterns, and the
value is in measuring how well a simple guard catches them and where it misses.
"""
from __future__ import annotations

import re

# Each category maps to patterns whose match is a signal of injection.
SIGNALS: dict[str, list[str]] = {
    "override_instructions": [
        r"\b(ignore|disregard|forget|override)\b[^.]{0,40}\b(previous|prior|above|earlier|all|system|your|the)\b[^.]{0,25}\b(instruction|instructions|prompt|rules|context|directions)\b",  # noqa: E501
        r"\byou are now\b",
        r"\bnew instructions?\s*:",
    ],
    "reveal_secrets": [
        r"\b(reveal|show|print|repeat|expose|leak|tell me)\b[^.]{0,40}\b(system prompt|your instructions|the prompt|api key|password|secret|credentials|hidden)\b",  # noqa: E501
    ],
    "exfiltration": [
        r"\b(send|forward|email|post|upload|exfiltrate|leak)\b[^.]{0,50}\bto\b[^.]{0,40}(https?://|@|external|attacker|evil|this address|my server)",  # noqa: E501
    ],
    "role_injection": [
        r"(?im)^\s*(system|assistant|developer)\s*:",
        r"<\|.*?\|>",
        r"\[/?(system|inst)\]",
        r"\bdeveloper mode\b",
    ],
    "destructive_command": [
        r"\brm\s+-rf\b",
        r"\bdrop\s+table\b",
        r"\bdelete\s+all\b",
        r"\bwire\s+(transfer|\$)",
    ],
}

_COMPILED = {cat: [re.compile(p, re.IGNORECASE) for p in pats] for cat, pats in SIGNALS.items()}


def detect(text: str, threshold: int = 1) -> dict:
    """Return the matched signal categories and whether the text is flagged."""
    categories = [cat for cat, pats in _COMPILED.items() if any(p.search(text) for p in pats)]
    return {
        "is_injection": len(categories) >= threshold,
        "score": len(categories),
        "categories": categories,
    }


def evaluate(dataset: list[dict], threshold: int = 1) -> dict:
    """Score the detector against labeled rows: {"text", "label": "benign"|"injection"}."""
    tp = fp = tn = fn = 0
    per_item = []
    for row in dataset:
        flagged = detect(row["text"], threshold)["is_injection"]
        actual = row["label"] == "injection"
        if flagged and actual:
            tp += 1
        elif flagged and not actual:
            fp += 1
        elif not flagged and actual:
            fn += 1
        else:
            tn += 1
        per_item.append({"id": row.get("id"), "label": row["label"], "flagged": flagged})

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    accuracy = (tp + tn) / len(dataset) if dataset else 0.0
    return {
        "threshold": threshold,
        "n": len(dataset),
        "confusion": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "accuracy": round(accuracy, 4),
        "per_item": per_item,
    }
