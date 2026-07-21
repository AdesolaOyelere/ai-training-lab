#!/usr/bin/env python3
"""Clean a raw dataset into SFT messages format and write the cleaned set + report.

    python run.py                 # uses raw.jsonl
    python run.py my_raw.jsonl
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from prepare import prepare

HERE = Path(__file__).parent


def load(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def write_report(report: dict, path: Path) -> None:
    order = [
        "input", "dropped_missing_field", "dropped_empty", "dropped_placeholder",
        "dropped_too_short", "dropped_too_long", "dropped_duplicate", "kept",
    ]
    lines = ["# SFT Data Prep — Report", "", "| Stage | Count |", "|---|---|"]
    for k in order:
        lines.append(f"| {k} | {report[k]} |")
    lines.append(f"| keep_rate | {report['keep_rate']:.3f} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    path = Path(argv[0]) if argv else HERE / "raw.jsonl"
    result = prepare(load(path))

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    with (out / "cleaned.jsonl").open("w", encoding="utf-8") as f:
        for rec in result["records"]:
            f.write(json.dumps(rec) + "\n")
    (out / "report.json").write_text(json.dumps(result["report"], indent=2), encoding="utf-8")
    write_report(result["report"], out / "report.md")

    for k, v in result["report"].items():
        print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
