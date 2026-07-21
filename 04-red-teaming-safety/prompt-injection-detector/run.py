#!/usr/bin/env python3
"""Evaluate the prompt-injection detector over a labeled dataset.

    python run.py                 # uses dataset.jsonl
    python run.py --threshold 2   # require 2 signal categories to flag
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from detector import evaluate

HERE = Path(__file__).parent


def load(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def write_report(m: dict, path: Path) -> None:
    c = m["confusion"]
    lines = [
        "# Prompt-Injection Detector — Evaluation",
        "",
        f"- Examples: **{m['n']}** · threshold: {m['threshold']} signal(s)",
        f"- Precision **{m['precision']:.3f}** · Recall **{m['recall']:.3f}** · "
        f"F1 **{m['f1']:.3f}** · Accuracy **{m['accuracy']:.3f}**",
        "",
        "| | flagged | not flagged |",
        "|---|---|---|",
        f"| **injection** | {c['tp']} (TP) | {c['fn']} (FN) |",
        f"| **benign** | {c['fp']} (FP) | {c['tn']} (TN) |",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dataset", default=str(HERE / "dataset.jsonl"))
    ap.add_argument("--threshold", type=int, default=1)
    args = ap.parse_args()

    metrics = evaluate(load(Path(args.dataset)), args.threshold)

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "results.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    write_report(metrics, out / "results.md")

    for k in ("precision", "recall", "f1", "accuracy"):
        print(f"{k}: {metrics[k]}")
    print(f"confusion: {metrics['confusion']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
