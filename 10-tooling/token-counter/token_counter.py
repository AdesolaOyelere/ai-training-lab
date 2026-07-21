"""Estimate token counts and API cost for text or a JSONL dataset.

Exact token counts require a model's own tokenizer, which is a heavy dependency. This
tool uses the widely cited rule of thumb that English text runs about **4 characters
per token**, then computes cost exactly from a per-model price table. It's meant for
budgeting and dataset sizing — fast, offline, and clearly an estimate.

Usage:
    python token_counter.py --text "hello world"
    python token_counter.py --file data.jsonl --fields prompt,response --model sonnet
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

# USD per 1M tokens (input, output). Illustrative round numbers, not a live price feed.
PRICES: dict[str, tuple[float, float]] = {
    "haiku": (0.80, 4.00),
    "sonnet": (3.00, 15.00),
    "opus": (15.00, 75.00),
}

_CHARS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    """Estimate tokens using the ~4-characters-per-token rule of thumb for English."""
    if not text:
        return 0
    return math.ceil(len(text) / _CHARS_PER_TOKEN)


def estimate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    if model not in PRICES:
        raise ValueError(f"unknown model: {model} (known: {', '.join(PRICES)})")
    in_price, out_price = PRICES[model]
    cost = input_tokens / 1_000_000 * in_price + output_tokens / 1_000_000 * out_price
    return round(cost, 6)


def analyze_dataset(rows: list[dict], fields: list[str], model: str) -> dict:
    input_tokens = 0
    for row in rows:
        for f in fields:
            if f in row and isinstance(row[f], str):
                input_tokens += estimate_tokens(row[f])
    return {
        "n_rows": len(rows),
        "fields": fields,
        "model": model,
        "input_tokens": input_tokens,
        "avg_tokens_per_row": round(input_tokens / len(rows), 2) if rows else 0.0,
        "estimated_input_cost_usd": estimate_cost(input_tokens, 0, model),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", help="estimate tokens for a literal string")
    src.add_argument("--file", help="a .jsonl dataset to size")
    ap.add_argument("--fields", default="text", help="comma-separated fields to count (for --file)")
    ap.add_argument("--model", default="sonnet", choices=list(PRICES))
    args = ap.parse_args(argv)

    if args.text is not None:
        n = estimate_tokens(args.text)
        cost = estimate_cost(n, 0, args.model)
        print(f"tokens (est): {n}")
        print(f"input cost @ {args.model}: ${cost:.6f}")
        return 0

    rows = [
        json.loads(line)
        for line in Path(args.file).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    stats = analyze_dataset(rows, [f.strip() for f in args.fields.split(",") if f.strip()], args.model)
    json.dump(stats, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
