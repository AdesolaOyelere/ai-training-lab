"""Measure how accuracy changes as you add few-shot exemplars.

This is a self-contained, deterministic ablation. The task is intent classification;
the "model" is a nearest-exemplar classifier: given k labeled exemplars it labels a
test item by its most similar exemplar (token Jaccard), and with zero exemplars it can
only fall back to the majority-class prior. That produces an honest few-shot curve —
accuracy rising with k — and demonstrates the ablation methodology (vary shots, hold
everything else fixed, report accuracy per condition) that you'd run against a real
model.
"""
from __future__ import annotations

import re
from collections import Counter

_WORD = re.compile(r"\w+")


def _tokens(text: str) -> set[str]:
    return set(_WORD.findall(text.lower()))


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def classify(text: str, exemplars: list[dict], prior_label: str) -> str:
    """Nearest-exemplar classification; falls back to the prior with no exemplars."""
    if not exemplars:
        return prior_label
    toks = _tokens(text)
    best, best_sim = prior_label, -1.0
    for ex in exemplars:
        sim = _jaccard(toks, _tokens(ex["text"]))
        if sim > best_sim:
            best_sim, best = sim, ex["label"]
    return best


def _prior(pool: list[dict]) -> str:
    return Counter(e["label"] for e in pool).most_common(1)[0][0]


def run_ablation(train: list[dict], test: list[dict], shots: list[int]) -> dict:
    """For each k in shots, use the first k train items as exemplars and score test."""
    prior = _prior(train)
    conditions = []
    for k in shots:
        exemplars = train[:k]
        correct = sum(1 for t in test if classify(t["text"], exemplars, prior) == t["label"])
        conditions.append({"shots": k, "accuracy": round(correct / len(test), 4) if test else 0.0})
    # summarize the trend
    accs = [c["accuracy"] for c in conditions]
    return {
        "n_test": len(test),
        "prior_label": prior,
        "conditions": conditions,
        "improvement_0_to_max": round(accs[-1] - accs[0], 4) if accs else 0.0,
        "monotonic_nondecreasing": all(accs[i] <= accs[i + 1] for i in range(len(accs) - 1)),
    }
