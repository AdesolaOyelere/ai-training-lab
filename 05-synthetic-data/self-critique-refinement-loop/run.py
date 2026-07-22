#!/usr/bin/env python3
"""Refine a deliberately flawed draft toward a constraint spec and show the trajectory.

    python run.py
"""
from __future__ import annotations

import json
from pathlib import Path

from refine import refine

HERE = Path(__file__).parent

# A draft that violates several constraints at once: too long, double spaces, no final
# period, and missing a required keyword ("safety").
DRAFT = "This  guide explains how the system works in considerable detail across many words"
SPEC = {
    "max_words": 12,
    "must_end_with_period": True,
    "must_include": ["safety"],
    "no_trailing_space": True,
}


def main() -> int:
    result = refine(DRAFT, SPEC)

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"converged: {result['converged']} in {result['iterations']} iteration(s)")
    for i, step in enumerate(result["trajectory"]):
        print(f"  iter {i}: {len(step['violations'])} violation(s) {step['violations']}")
    print(f"final: {result['final_text']!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
