#!/usr/bin/env python3
"""Evaluate PII detection over a labeled dataset and show a redaction example.

    python run.py
"""
from __future__ import annotations

import json
from pathlib import Path

from pii import evaluate, find_pii, redact

HERE = Path(__file__).parent


def main() -> int:
    rows = [
        json.loads(x)
        for x in (HERE / "dataset.jsonl").read_text(encoding="utf-8").splitlines()
        if x.strip()
    ]
    metrics = evaluate(rows)

    # count PII by type across the whole set for the report
    by_type: dict[str, int] = {}
    for r in rows:
        for span in find_pii(r["text"]):
            by_type[span["type"]] = by_type.get(span["type"], 0) + 1

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    example = "Contact jane.doe@example.com or (555) 123-4567."
    report = {"metrics": metrics, "pii_counts_by_type": by_type, "redaction_example": redact(example)}
    (out / "results.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    print(f"precision {metrics['precision']} recall {metrics['recall']} f1 {metrics['f1']}")
    print(f"by type: {by_type}")
    print(f"redaction: {report['redaction_example']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
