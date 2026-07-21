"""Rubric scoring for summary-quality annotation.

An annotation handbook (HANDBOOK.md) defines how to rate a summary on four
dimensions. This module turns those per-dimension scores into a single decision and
checks annotator ratings against gold calibration examples, so the guideline is not
just prose — it is executable and testable.

Dimensions (each scored 1-4, see HANDBOOK.md):
    coverage      - are the key points present
    faithfulness  - is everything stated supported by the source (no hallucination)
    conciseness   - free of redundancy and filler
    fluency       - grammatical and readable

Faithfulness is a gate: a summary that invents facts cannot be "accept", however
well it scores elsewhere.
"""
from __future__ import annotations

from dataclasses import dataclass

DIMENSIONS = ("coverage", "faithfulness", "conciseness", "fluency")
_MIN, _MAX = 1, 4
# Weights reflect what matters most for a usable summary.
WEIGHTS = {"coverage": 0.35, "faithfulness": 0.35, "conciseness": 0.15, "fluency": 0.15}


@dataclass(frozen=True)
class Rating:
    coverage: int
    faithfulness: int
    conciseness: int
    fluency: int

    def as_dict(self) -> dict:
        return {d: getattr(self, d) for d in DIMENSIONS}


def validate(rating: dict) -> None:
    for d in DIMENSIONS:
        if d not in rating:
            raise ValueError(f"missing dimension: {d}")
        v = rating[d]
        if not isinstance(v, int) or isinstance(v, bool) or not (_MIN <= v <= _MAX):
            raise ValueError(f"{d} must be an int in [{_MIN}, {_MAX}], got {v!r}")


def weighted_score(rating: dict) -> float:
    validate(rating)
    return round(sum(WEIGHTS[d] * rating[d] for d in DIMENSIONS), 4)


def decision(rating: dict) -> str:
    """Map a rating to accept / revise / reject, with faithfulness as a hard gate."""
    validate(rating)
    if rating["faithfulness"] <= 1:
        return "reject"  # hallucination is disqualifying regardless of other scores
    score = weighted_score(rating)
    # Accept needs a summary that is faithful, adequately complete, and high overall.
    if rating["faithfulness"] >= 3 and rating["coverage"] >= 3 and score >= 3.0:
        return "accept"
    if score >= 2.0:
        return "revise"
    return "reject"


def score_against_gold(gold: list[dict]) -> dict:
    """Check that decision() reproduces the gold labels; report any mismatches."""
    mismatches = []
    for ex in gold:
        got = decision(ex["rating"])
        if got != ex["label"]:
            mismatches.append({"id": ex.get("id"), "expected": ex["label"], "got": got})
    n = len(gold)
    return {
        "n": n,
        "agreement": round((n - len(mismatches)) / n, 4) if n else 1.0,
        "mismatches": mismatches,
    }
