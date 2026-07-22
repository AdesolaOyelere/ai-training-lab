#!/usr/bin/env python3
"""Verify citation-grounded QA over a dataset.

    python run.py
"""
from __future__ import annotations

import json
from pathlib import Path

from verify import evaluate

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

    print(f"grounded rate: {m['grounded_rate']}  mean support: {m['mean_support']}  "
          f"items with invalid citations: {m['n_with_invalid_citations']}")
    for r in m["per_item"]:
        print(f"  {r['id']}: grounded={r['grounded']} support={r['support']} invalid={r['invalid_citations']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
