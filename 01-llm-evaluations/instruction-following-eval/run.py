#!/usr/bin/env python3
"""Run the instruction-following eval and write results.

Examples:
    python run.py                      # mock provider (offline, reproducible)
    python run.py --live               # live Anthropic model (needs ANTHROPIC_API_KEY)
    python run.py --report             # also write results/results.md
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from eval import load_dataset, run_eval
from providers import anthropic_provider, mock_provider

HERE = Path(__file__).parent


def write_report(results: dict, path: Path) -> None:
    lines = [
        "# Instruction-Following Eval — Results",
        "",
        f"- Items: **{results['n_items']}**",
        f"- Mean constraint satisfaction: **{results['mean_constraint_satisfaction']:.3f}**",
        f"- Perfect rate (all constraints pass): **{results['perfect_rate']:.3f}**",
        "",
        "| Item | Passed / Total | Failed constraints |",
        "|---|---|---|",
    ]
    for r in results["items"]:
        failed = [c["constraint"] for c in r["checks"] if not c["passed"]]
        failed_txt = ", ".join(failed) if failed else "—"
        lines.append(f"| `{r['id']}` | {r['n_passed']}/{r['n_constraints']} | {failed_txt} |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dataset", default=str(HERE / "dataset.jsonl"))
    ap.add_argument("--live", action="store_true", help="use a live Anthropic model")
    ap.add_argument("--model", default="claude-sonnet-5")
    ap.add_argument("--report", action="store_true", help="write results/results.md")
    args = ap.parse_args()

    items = load_dataset(args.dataset)

    if args.live:
        generate = anthropic_provider(model=args.model)
    else:
        if not any(it.mock_response for it in items):
            raise SystemExit("dataset has no mock responses; use --live")
        generate = mock_provider({it.prompt: it.mock_response for it in items})

    results = run_eval(items, generate)

    out_dir = HERE / "results"
    out_dir.mkdir(exist_ok=True)
    (out_dir / "results.json").write_text(json.dumps(results, indent=2), encoding="utf-8")
    if args.report:
        write_report(results, out_dir / "results.md")

    print(f"items: {results['n_items']}")
    print(f"mean constraint satisfaction: {results['mean_constraint_satisfaction']:.3f}")
    print(f"perfect rate: {results['perfect_rate']:.3f}")
    return 0


if __name__ == "__main__":
    os.chdir(HERE)  # so relative default paths resolve when invoked from anywhere
    raise SystemExit(main())
