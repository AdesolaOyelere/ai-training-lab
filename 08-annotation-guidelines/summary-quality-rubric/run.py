#!/usr/bin/env python3
"""Check the rubric against the gold calibration set and print a summary.

    python run.py
"""
from __future__ import annotations

import json
from pathlib import Path

from rubric import decision, score_against_gold, weighted_score

HERE = Path(__file__).parent


def main() -> int:
    gold = json.loads((HERE / "gold_examples.json").read_text(encoding="utf-8"))
    report = score_against_gold(gold)

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    detail = [
        {"id": ex["id"], "score": weighted_score(ex["rating"]), "decision": decision(ex["rating"]),
         "gold": ex["label"]}
        for ex in gold
    ]
    (out / "results.json").write_text(
        json.dumps({"report": report, "detail": detail}, indent=2), encoding="utf-8"
    )

    print(f"gold examples: {report['n']}")
    print(f"rule/label agreement: {report['agreement']:.3f}")
    if report["mismatches"]:
        print(f"mismatches: {report['mismatches']}")
    else:
        print("all gold labels reproduced by the documented rules")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
