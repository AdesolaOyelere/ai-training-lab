#!/usr/bin/env python3
"""Compute inter-annotator agreement from a JSONL of annotation rows.

Each row is {"item": ..., "annotator": ..., "label": ...}.

    python run.py                       # uses sample_data/annotations.jsonl
    python run.py path/to/annotations.jsonl
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from agreement import analyze

HERE = Path(__file__).parent


def load_rows(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_report(stats: dict, path: Path) -> None:
    def fmt(v):
        return "n/a" if v is None else v

    lines = [
        "# Inter-Annotator Agreement — Report",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Items | {stats['n_items']} |",
        f"| Annotators | {stats['n_annotators']} |",
        f"| Categories | {', '.join(map(str, stats['categories']))} |",
        f"| Mean percent agreement | {fmt(stats['mean_percent_agreement'])} |",
        f"| Mean pairwise Cohen's kappa | {fmt(stats['mean_pairwise_cohens_kappa'])} |",
        f"| Fleiss' kappa | {fmt(stats['fleiss_kappa'])} |",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    path = Path(argv[0]) if argv else HERE / "sample_data" / "annotations.jsonl"
    stats = analyze(load_rows(path))

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "report.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    write_report(stats, out / "report.md")

    for k, v in stats.items():
        print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
