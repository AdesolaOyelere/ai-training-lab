"""Convert preference data between the common RLHF formats.

Preference datasets come in a few shapes and different trainers want different ones:

- "pairwise"  -> {"prompt", "chosen", "rejected"}                (one comparison)
- "ranked"    -> {"prompt", "responses": [best, ..., worst]}     (a full ranking)
- "binary"    -> {"prompt", "completion", "label": bool}         (KTO-style, one per row)

Everything normalizes to a ranked list of responses (best first), so any format can be
produced from any other. The interesting transform is ranked -> pairwise, which expands
a ranking of N responses into all ordered better/worse pairs — a real preprocessing
step when turning ranked human data into pairwise training examples.
"""
from __future__ import annotations

from itertools import combinations

FORMATS = ("pairwise", "ranked", "binary")


def to_ranked(record: dict, fmt: str) -> dict:
    """Normalize any format to {"prompt", "responses": [best..worst]}."""
    if fmt == "ranked":
        if not record.get("responses"):
            raise ValueError("ranked record needs a non-empty 'responses' list")
        return {"prompt": record["prompt"], "responses": list(record["responses"])}
    if fmt == "pairwise":
        return {"prompt": record["prompt"], "responses": [record["chosen"], record["rejected"]]}
    if fmt == "binary":
        # a single binary row only tells us one response is (un)desirable; represent it
        # as a one-element ranking tagged with its label for round-tripping.
        return {
            "prompt": record["prompt"],
            "responses": [record["completion"]],
            "_binary_label": bool(record["label"]),
        }
    raise ValueError(f"unknown format: {fmt}")


def from_ranked(norm: dict, fmt: str) -> list[dict]:
    """Emit records in the target format from a normalized ranking."""
    prompt, responses = norm["prompt"], norm["responses"]
    if fmt == "ranked":
        return [{"prompt": prompt, "responses": list(responses)}]
    if fmt == "pairwise":
        if len(responses) < 2:
            raise ValueError("need at least 2 responses to form a pairwise comparison")
        # all ordered pairs: earlier (better) is chosen over later (worse)
        return [
            {"prompt": prompt, "chosen": responses[i], "rejected": responses[j]}
            for i, j in combinations(range(len(responses)), 2)
        ]
    if fmt == "binary":
        if "_binary_label" in norm and len(responses) == 1:
            return [{"prompt": prompt, "completion": responses[0], "label": norm["_binary_label"]}]
        # top half of the ranking is desirable (True), bottom half undesirable (False)
        n = len(responses)
        cutoff = (n + 1) // 2
        return [
            {"prompt": prompt, "completion": r, "label": idx < cutoff}
            for idx, r in enumerate(responses)
        ]
    raise ValueError(f"unknown format: {fmt}")


def convert_record(record: dict, src: str, dst: str) -> list[dict]:
    return from_ranked(to_ranked(record, src), dst)


def convert(records: list[dict], src: str, dst: str) -> list[dict]:
    out: list[dict] = []
    for i, rec in enumerate(records):
        try:
            out.extend(convert_record(rec, src, dst))
        except (KeyError, ValueError) as exc:
            raise ValueError(f"record {i}: {exc}") from exc
    return out
