#!/usr/bin/env python3
"""Evaluate JSON schema adherence over a set of model outputs.

    python run.py
"""
from __future__ import annotations

import json
from pathlib import Path

from schema_eval import evaluate

HERE = Path(__file__).parent


def main() -> int:
    schema = json.loads((HERE / "schema.json").read_text(encoding="utf-8"))
    outputs = [
        json.loads(x)["output"]
        for x in (HERE / "dataset.jsonl").read_text(encoding="utf-8").splitlines()
        if x.strip()
    ]
    metrics = evaluate(outputs, schema)

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "results.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    print(f"conformance rate: {metrics['conformance_rate']} ({metrics['n_conformant']}/{metrics['n']})")
    print(f"failure reasons: {metrics['failure_reasons']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
