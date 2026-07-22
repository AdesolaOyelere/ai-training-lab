#!/usr/bin/env python3
"""Run the few-shot ablation and write the accuracy-vs-shots curve.

    python run.py
"""
from __future__ import annotations

import json
from pathlib import Path

from ablation import run_ablation
from data import TEST, TRAIN

HERE = Path(__file__).parent


def main() -> int:
    result = run_ablation(TRAIN, TEST, shots=[0, 1, 3, 6, 9])

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "results.json").write_text(json.dumps(result, indent=2), encoding="utf-8")

    print(f"prior label: {result['prior_label']}  (used at 0 shots)")
    for c in result["conditions"]:
        print(f"  {c['shots']:>2} shots -> accuracy {c['accuracy']:.3f}")
    print(f"improvement 0 -> max shots: +{result['improvement_0_to_max']:.3f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
