#!/usr/bin/env python3
"""Generate a verified reasoning-trace dataset and write it to results/.

    python run.py                 # defaults (n=200, seed=7)
    python run.py --n 500 --seed 3 --flaw-rate 0.2
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from pipeline import FLAW_RATE, MIN_STEPS, SEED, N, run_pipeline

HERE = Path(__file__).parent


def write_report(stats: dict, path: Path) -> None:
    lines = [
        "# Reasoning-Trace Generator — Report",
        "",
        "| Stage | Count |",
        "|---|---|",
        f"| Generated | {stats['generated']} |",
        f"| Removed as duplicates | {stats['duplicates_removed']} |",
        f"| Rejected (too short) | {stats['rejected_short']} |",
        f"| Rejected (wrong answer) | {stats['rejected_wrong_answer']} |",
        f"| **Accepted** | **{stats['accepted']}** |",
        f"| Acceptance rate | {stats['acceptance_rate']:.1%} |",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--n", type=int, default=N)
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--flaw-rate", type=float, default=FLAW_RATE)
    ap.add_argument("--min-steps", type=int, default=MIN_STEPS)
    args = ap.parse_args()

    accepted, stats = run_pipeline(args.n, args.seed, args.flaw_rate, args.min_steps)

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    with (out / "accepted.jsonl").open("w", encoding="utf-8") as f:
        for rec in accepted:
            f.write(json.dumps(rec) + "\n")
    (out / "report.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    write_report(stats, out / "report.md")

    for k, v in stats.items():
        print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    import os

    os.chdir(HERE)
    raise SystemExit(main())
