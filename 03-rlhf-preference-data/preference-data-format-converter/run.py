#!/usr/bin/env python3
"""Convert the sample ranked data into pairwise and binary formats.

    python run.py
"""
from __future__ import annotations

import json
from pathlib import Path

from convert import convert

HERE = Path(__file__).parent


def load(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def main() -> int:
    ranked = load(HERE / "sample_data" / "ranked.jsonl")
    pairwise = convert(ranked, "ranked", "pairwise")
    binary = convert(ranked, "ranked", "binary")

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    summary = {
        "n_ranked": len(ranked),
        "n_pairwise": len(pairwise),
        "n_binary": len(binary),
        "pairwise_sample": pairwise[0],
        "binary_sample": binary[0],
    }
    (out / "results.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"{len(ranked)} ranked records -> {len(pairwise)} pairwise comparisons, {len(binary)} binary rows")
    print(f"first pairwise: {pairwise[0]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
