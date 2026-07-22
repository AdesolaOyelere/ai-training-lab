#!/usr/bin/env python3
"""Score a set of agent trajectories against their tasks.

    python run.py
"""
from __future__ import annotations

import json
from pathlib import Path

from scorer import evaluate

HERE = Path(__file__).parent


def main() -> int:
    pairs = json.loads((HERE / "trajectories.json").read_text(encoding="utf-8"))
    metrics = evaluate(pairs)

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "results.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"mean overall: {metrics['mean_overall']}")
    for r in metrics["per_trajectory"]:
        print(f"  {r['id']}: success {r['success']} eff {r['efficiency']} "
              f"valid {r['validity']} no_loops {r['no_loops']} -> overall {r['overall']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
