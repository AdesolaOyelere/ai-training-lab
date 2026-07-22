"""Self-consistency: majority vote over several sampled answers.

Self-consistency prompting samples multiple reasoning chains for the same question and
takes the majority answer, which is more reliable than any single sample when the model
is right more often than it is wrong in any one specific way. This module implements the
voting and measures majority-vote accuracy against single-sample accuracy over a dataset
of sampled answers, so the benefit is quantified rather than assumed.

Answers are normalized before counting so "1,200", "1200", and " 1200 " vote together.
"""
from __future__ import annotations

import re
from collections import Counter


def normalize(answer: str) -> str:
    a = answer.strip().lower()
    a = re.sub(r"[$,]", "", a)
    a = re.sub(r"\s+", " ", a)
    return a.rstrip(".")


def majority_vote(samples: list[str]) -> tuple[str, float]:
    """Return (winning_answer_normalized, agreement_fraction). Ties break toward the
    first-seen answer among those tied (deterministic)."""
    if not samples:
        return "", 0.0
    norm = [normalize(s) for s in samples]
    counts = Counter(norm)
    top = max(counts.values())
    # deterministic tie-break: earliest in the sample order among the tied winners
    for n in norm:
        if counts[n] == top:
            return n, round(top / len(samples), 4)
    return norm[0], round(top / len(samples), 4)


def evaluate(items: list[dict]) -> dict:
    """items: [{id, gold, samples: [str]}]. Compares single-sample vs majority vote."""
    n = len(items)
    single_correct = 0   # counts the first sample as the "single sample"
    single_expected = 0.0  # expected accuracy if you drew one sample at random
    vote_correct = 0
    per_item = []
    for it in items:
        gold = normalize(it["gold"])
        samples = it["samples"]
        norm = [normalize(s) for s in samples]

        first_ok = norm[0] == gold
        single_correct += first_ok
        single_expected += sum(1 for x in norm if x == gold) / len(norm)

        winner, agreement = majority_vote(samples)
        vote_ok = winner == gold
        vote_correct += vote_ok

        per_item.append({
            "id": it.get("id"),
            "vote": winner,
            "vote_correct": vote_ok,
            "agreement": agreement,
            "first_sample_correct": first_ok,
        })
    return {
        "n": n,
        "single_sample_accuracy_first": round(single_correct / n, 4) if n else 0.0,
        "single_sample_accuracy_expected": round(single_expected / n, 4) if n else 0.0,
        "majority_vote_accuracy": round(vote_correct / n, 4) if n else 0.0,
        "per_item": per_item,
    }
