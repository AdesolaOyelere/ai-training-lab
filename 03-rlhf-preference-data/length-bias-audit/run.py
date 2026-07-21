#!/usr/bin/env python3
"""Audit a preference dataset (chosen/rejected pairs) for length bias.

    python run.py                 # uses dataset.jsonl
    python run.py my_pairs.jsonl
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from audit import audit

HERE = Path(__file__).parent


def load(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def main(argv: list[str]) -> int:
    path = Path(argv[0]) if argv else HERE / "dataset.jsonl"
    report = audit(load(path))

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    for k, v in report.items():
        print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
