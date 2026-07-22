#!/usr/bin/env python3
"""Evaluate the tiered risk classifier over a labeled dataset.

    python run.py
"""
from __future__ import annotations

import json
from pathlib import Path

from classifier import evaluate

HERE = Path(__file__).parent


def main() -> int:
    rows = [
        json.loads(x)
        for x in (HERE / "dataset.jsonl").read_text(encoding="utf-8").splitlines()
        if x.strip()
    ]
    metrics = evaluate(rows)

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "results.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"accuracy: {metrics['accuracy']} ({metrics['n']} requests)")
    print(f"per-tier recall: {metrics['per_tier_recall']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
