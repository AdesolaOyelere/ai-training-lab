#!/usr/bin/env python3
"""Evaluate summary quality over a dataset of {source, key_points, summary}.

    python run.py
"""
from __future__ import annotations

import json
from pathlib import Path

from summ_eval import evaluate

HERE = Path(__file__).parent


def main() -> int:
    items = [
        json.loads(x)
        for x in (HERE / "dataset.jsonl").read_text(encoding="utf-8").splitlines()
        if x.strip()
    ]
    metrics = evaluate(items)

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "results.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"mean coverage {metrics['mean_coverage']}  faithfulness {metrics['mean_faithfulness']}  "
          f"conciseness {metrics['mean_conciseness']}  overall {metrics['mean_overall']}")
    for r in metrics["per_item"]:
        print(f"  {r['id']}: cov {r['coverage']} faith {r['faithfulness']} conc {r['conciseness']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
