#!/usr/bin/env python3
"""Build a stratified, leakage-safe split of a synthetic labeled dataset.

    python run.py
"""
from __future__ import annotations

import json
from pathlib import Path

from split import report, split

HERE = Path(__file__).parent


def make_dataset() -> list[dict]:
    """20 rows across 2 labels, with a couple of duplicate texts to exercise leakage
    prevention (the duplicates must not span splits)."""
    rows = []
    for i in range(10):
        rows.append({"text": f"positive review number {i} great product", "label": "pos"})
        rows.append({"text": f"negative review number {i} poor quality", "label": "neg"})
    # inject duplicates of two existing texts
    rows.append({"text": "positive review number 0 great product", "label": "pos"})
    rows.append({"text": "negative review number 0 poor quality", "label": "neg"})
    return rows


def main() -> int:
    rows = make_dataset()
    splits = split(rows, ratios=(0.6, 0.2, 0.2), seed=0)
    rep = report(rows, splits)

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "results.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")

    print(f"total {rep['total']} -> sizes {rep['sizes']}")
    print(f"overall label props: {rep['overall_label_props']}")
    print(f"per-split label props: {rep['split_label_props']}")
    print(f"no leakage: {rep['no_leakage']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
