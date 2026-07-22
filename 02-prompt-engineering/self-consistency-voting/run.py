#!/usr/bin/env python3
"""Compare single-sample vs majority-vote (self-consistency) accuracy.

    python run.py
"""
from __future__ import annotations

import json
from pathlib import Path

from voting import evaluate

HERE = Path(__file__).parent


def main() -> int:
    items = [
        json.loads(x)
        for x in (HERE / "dataset.jsonl").read_text(encoding="utf-8").splitlines()
        if x.strip()
    ]
    m = evaluate(items)

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "results.json").write_text(json.dumps(m, indent=2), encoding="utf-8")

    print(f"single-sample accuracy (first):    {m['single_sample_accuracy_first']}")
    print(f"single-sample accuracy (expected): {m['single_sample_accuracy_expected']}")
    print(f"majority-vote accuracy:            {m['majority_vote_accuracy']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
