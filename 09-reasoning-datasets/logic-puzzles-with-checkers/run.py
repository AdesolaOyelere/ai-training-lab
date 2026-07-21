#!/usr/bin/env python3
"""Solve each puzzle via its checker and confirm the solution is unique.

    python run.py
"""
from __future__ import annotations

import json
from pathlib import Path

from puzzles import PUZZLES, check, unique_solution

HERE = Path(__file__).parent


def main() -> int:
    report = {}
    for name in PUZZLES:
        sol = unique_solution(name)
        report[name] = {
            "solution": sol,
            "unique": sol is not None,
            "checker_confirms": check(name, sol) if sol is not None else False,
        }

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    for name, r in report.items():
        print(f"{name}: solution={r['solution']} unique={r['unique']} confirmed={r['checker_confirms']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
