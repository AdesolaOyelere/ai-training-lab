#!/usr/bin/env python3
"""Lint a JSONL of prompts and write a quality report.

    python run.py                 # uses prompts.jsonl
    python run.py my_prompts.jsonl
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from linter import lint

HERE = Path(__file__).parent


def load(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def write_report(results: list[dict], path: Path) -> None:
    avg = sum(r["score"] for r in results) / len(results) if results else 0
    lines = [
        "# Prompt Linter — Report",
        "",
        f"- Prompts: **{len(results)}** · average score: **{avg:.1f}/100**",
        "",
        "| Prompt | Score | Issues |",
        "|---|---|---|",
    ]
    for r in results:
        rules = ", ".join(i["rule"] for i in r["issues"]) or "—"
        lines.append(f"| `{r['id']}` | {r['score']} | {rules} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    path = Path(argv[0]) if argv else HERE / "prompts.jsonl"
    results = []
    for row in load(path):
        report = lint(row["prompt"])
        results.append({"id": row.get("id"), "note": row.get("note"), **report})

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "report.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    write_report(results, out / "report.md")

    for r in results:
        print(f"{r['id']}: score={r['score']} issues={len(r['issues'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
