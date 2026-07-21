"""Audit a preference dataset for length bias.

Reward models trained on human preferences often learn a shortcut: prefer the longer
answer. That starts in the data, when annotators systematically pick the longer
response regardless of quality. This module measures how strong that signal is in a
chosen/rejected dataset, so you can catch it before it becomes a reward-model artifact.

Metrics:
- longer_chosen_rate  - fraction of pairs where the chosen answer is longer
- mean_length_delta   - mean (chosen_len - rejected_len) in tokens
- point_biserial      - correlation between "chosen" and length across all responses
- a plain-language verdict with a suggested guard
"""
from __future__ import annotations

import math
import re

_WORD = re.compile(r"\w+")


def token_len(text: str) -> int:
    return len(_WORD.findall(text))


def _point_biserial(labels: list[int], values: list[float]) -> float:
    """Correlation between a binary label (1=chosen, 0=rejected) and a numeric value.

    Equivalent to Pearson's r with a 0/1 variable; 0 means length carries no signal
    about which response was chosen."""
    n = len(labels)
    if n == 0:
        return 0.0
    mean_v = sum(values) / n
    mean_l = sum(labels) / n
    cov = sum((labels[i] - mean_l) * (values[i] - mean_v) for i in range(n))
    var_l = sum((x - mean_l) ** 2 for x in labels)
    var_v = sum((x - mean_v) ** 2 for x in values)
    if var_l == 0 or var_v == 0:
        return 0.0
    return cov / math.sqrt(var_l * var_v)


def audit(pairs: list[dict]) -> dict:
    """pairs: [{chosen, rejected}]. Returns length-bias metrics and a verdict."""
    n = len(pairs)
    if n == 0:
        return {"n": 0, "verdict": "no data"}

    longer_chosen = 0
    deltas: list[int] = []
    labels: list[int] = []
    lengths: list[float] = []
    for p in pairs:
        cl, rl = token_len(p["chosen"]), token_len(p["rejected"])
        deltas.append(cl - rl)
        if cl > rl:
            longer_chosen += 1
        labels.extend([1, 0])
        lengths.extend([cl, rl])

    longer_rate = longer_chosen / n
    r = _point_biserial(labels, lengths)

    if longer_rate >= 0.75 or r >= 0.35:
        verdict = "strong length bias — length-balance the data or add a length penalty"
    elif longer_rate >= 0.6 or r >= 0.2:
        verdict = "moderate length bias — worth checking before training a reward model"
    else:
        verdict = "no strong length bias detected"

    return {
        "n": n,
        "longer_chosen_rate": round(longer_rate, 4),
        "mean_length_delta": round(sum(deltas) / n, 4),
        "point_biserial": round(r, 4),
        "verdict": verdict,
    }
