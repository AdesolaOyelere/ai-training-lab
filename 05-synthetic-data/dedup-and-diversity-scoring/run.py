#!/usr/bin/env python3
"""Deduplicate a text dataset and report diversity before/after.

    python run.py                     # uses dataset.jsonl
    python run.py --threshold 0.7
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from dedup import analyze

HERE = Path(__file__).parent


def load(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def write_report(rows: list[dict], m: dict, path: Path) -> None:
    lines = [
        "# Dedup & Diversity — Report",
        "",
        f"- In: **{m['n_in']}** · kept: **{m['n_kept']}** · removed: **{m['n_removed']}**",
        f"- Diversity before: **{m['diversity_before']:.3f}** -> after: **{m['diversity_after']:.3f}**",
        "",
        "| Removed | Duplicate of |",
        "|---|---|",
    ]
    for r in m["removed"]:
        lines.append(f"| `{rows[r['index']]['id']}` | `{rows[r['duplicate_of']]['id']}` |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dataset", default=str(HERE / "dataset.jsonl"))
    ap.add_argument("--threshold", type=float, default=0.6)
    args = ap.parse_args()

    rows = load(Path(args.dataset))
    m = analyze([r["text"] for r in rows], threshold=args.threshold)

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "results.json").write_text(json.dumps(m, indent=2), encoding="utf-8")
    write_report(rows, m, out / "results.md")

    print(f"kept {m['n_kept']}/{m['n_in']}, removed {m['n_removed']}")
    print(f"diversity: {m['diversity_before']} -> {m['diversity_after']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
