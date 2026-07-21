#!/usr/bin/env python3
"""Run the pairwise judge with order-swap debiasing and write results.

    python run.py    # deterministic mock judge over dataset.jsonl
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from judge import Pair, first_position_judge, run_judgements

HERE = Path(__file__).parent


def load_pairs(path: Path) -> tuple[list[Pair], dict[str, str]]:
    pairs, prefers = [], {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        pairs.append(Pair(d["id"], d["question"], d["answer_a"], d["answer_b"]))
        if d.get("mock_biased"):
            prefers[d["question"]] = "A"
    return pairs, prefers


def write_report(m: dict, path: Path) -> None:
    lines = [
        "# LLM-as-Judge (Debiased) — Results",
        "",
        f"- Pairs: **{m['n']}**",
        f"- Model-A win rate: **{m['a_win_rate']:.3f}** · Model-B win rate: **{m['b_win_rate']:.3f}** · "
        f"Tie rate: **{m['tie_rate']:.3f}**",
        f"- Position-bias rate (verdict flipped when order swapped): **{m['position_bias_rate']:.3f}**",
        "",
        "| Pair | Winner | Consistent | Order1 | Order2 | Position bias |",
        "|---|---|---|---|---|---|",
    ]
    for r in m["results"]:
        lines.append(
            f"| `{r['id']}` | {r['winner']} | {'Y' if r['consistent'] else 'N'} | "
            f"{r['order1_favored']} | {r['order2_favored']} | {'Y' if r['position_bias'] else '-'} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dataset", default=str(HERE / "dataset.jsonl"))
    args = ap.parse_args()

    pairs, prefers = load_pairs(Path(args.dataset))
    metrics = run_judgements(pairs, first_position_judge(prefers))

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "results.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    write_report(metrics, out / "results.md")

    for k in ("a_win_rate", "b_win_rate", "tie_rate", "position_bias_rate"):
        print(f"{k}: {metrics[k]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
