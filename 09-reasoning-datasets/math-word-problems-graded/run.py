#!/usr/bin/env python3
"""Grade model outputs against the reasoning dataset.

    python run.py    # grades model_outputs.jsonl against dataset.jsonl
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from grader import grade_dataset

HERE = Path(__file__).parent


def load(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def write_report(m: dict, path: Path) -> None:
    lines = [
        "# Math Word Problems — Grading Report",
        "",
        f"- Problems: **{m['n']}** · overall accuracy: **{m['accuracy']:.3f}**",
        "",
        "| Answer type | Accuracy |",
        "|---|---|",
    ]
    for t, acc in m["accuracy_by_type"].items():
        lines.append(f"| {t} | {acc:.3f} |")
    lines += ["", "| Problem | Type | Correct |", "|---|---|---|"]
    for r in m["per_item"]:
        lines.append(f"| `{r['id']}` | {r['answer_type']} | {'Y' if r['correct'] else 'N'} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dataset", default=str(HERE / "dataset.jsonl"))
    ap.add_argument("--outputs", default=str(HERE / "model_outputs.jsonl"))
    args = ap.parse_args()

    items = load(Path(args.dataset))
    answers = {r["id"]: r["output"] for r in load(Path(args.outputs))}
    metrics = grade_dataset(items, answers)

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "results.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    write_report(metrics, out / "results.md")

    print(f"accuracy: {metrics['accuracy']}")
    print(f"by type: {metrics['accuracy_by_type']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
