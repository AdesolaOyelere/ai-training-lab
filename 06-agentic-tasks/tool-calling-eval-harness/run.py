#!/usr/bin/env python3
"""Run the tool-calling eval and write results.

    python run.py           # scores the committed mock agent over tasks.jsonl
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from harness import mock_agent, run_harness

HERE = Path(__file__).parent


def load_tasks(path: Path) -> list[dict]:
    return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]


def write_report(m: dict, path: Path) -> None:
    lines = [
        "# Tool-Calling Eval — Results",
        "",
        f"- Tasks: **{m['n_tasks']}**",
        f"- Valid-call rate: **{m['valid_rate']:.3f}**",
        f"- Tool-selection accuracy: **{m['tool_selection_accuracy']:.3f}**",
        f"- Arg match (given correct tool): **{m['arg_match_given_correct_tool']:.3f}**",
        f"- Full pass rate: **{m['full_pass_rate']:.3f}**",
        "",
        "| Task | valid | tool | args | fully | errors |",
        "|---|---|---|---|---|---|",
    ]
    for r in m["tasks"]:
        errs = "; ".join(r["errors"]) if r["errors"] else "—"
        lines.append(
            f"| `{r['id']}` | {'Y' if r['valid'] else 'N'} | {'Y' if r['tool_correct'] else 'N'} | "
            f"{'Y' if r['args_correct'] else 'N'} | {'Y' if r['fully_correct'] else 'N'} | {errs} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tasks", default=str(HERE / "tasks.jsonl"))
    args = ap.parse_args()

    tasks = load_tasks(Path(args.tasks))
    agent = mock_agent({t["prompt"]: {"tool": t["mock_tool"], "args": t["mock_args"]} for t in tasks})
    metrics = run_harness(tasks, agent)

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "results.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    write_report(metrics, out / "results.md")

    for k in ("valid_rate", "tool_selection_accuracy", "arg_match_given_correct_tool", "full_pass_rate"):
        print(f"{k}: {metrics[k]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
