#!/usr/bin/env python3
"""Route the gold examples through the edge-case detector and report coverage.

    python run.py
"""
from __future__ import annotations

import json
from pathlib import Path

from catalog import detect_edge_cases, route

HERE = Path(__file__).parent


def main() -> int:
    gold = json.loads((HERE / "gold_examples.json").read_text(encoding="utf-8"))
    report = route([{"id": g["id"], "text": g["text"]} for g in gold])

    # agreement with the pinned expected routing
    mismatches = [g["id"] for g in gold if detect_edge_cases(g["text"]) != sorted(g["expected"])]
    report["gold_mismatches"] = mismatches

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"flagged {report['flagged_for_review']}/{report['n']} for review")
    print(f"counts by case: {report['counts_by_case']}")
    print(f"gold mismatches: {mismatches or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
