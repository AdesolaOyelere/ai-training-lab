#!/usr/bin/env python3
"""Run the ReAct agent over a set of questions and write traces.

    python run.py
"""
from __future__ import annotations

import json
from pathlib import Path

from agent import rule_based_policy, run

HERE = Path(__file__).parent

QUESTIONS = [
    "What is 12 * (3 + 4)?",
    "What is the capital of France?",
    "What is the largest planet?",
    "How many words are here: the quick brown fox jumps",
    "What is the meaning of life?",
]


def main() -> int:
    traces = [run(q, rule_based_policy).as_dict() for q in QUESTIONS]

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "traces.json").write_text(json.dumps(traces, indent=2), encoding="utf-8")

    for t in traces:
        n = len(t["steps"])
        print(f"Q: {t['question']}\n  -> {t['answer']}  ({n} step(s), {t['stopped_reason']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
