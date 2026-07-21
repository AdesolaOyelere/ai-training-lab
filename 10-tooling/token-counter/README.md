# Token & Cost Counter

> Estimate token counts and compute exact API cost for a string or a whole JSONL
> dataset — fast, offline, and honest about being an estimate.

**Category:** `10-tooling` · **Skills:** CLI design, cost estimation, tokenization, Python

## Problem

Before you run a dataset through a model you want to know two things: roughly how many
tokens it is, and what that will cost. Exact counts need the model's own tokenizer (a
heavy dependency), but for budgeting and dataset sizing a good, transparent estimate is
enough — and the cost math, given a token count, is exact.

## Approach

`token_counter.py` estimates tokens with the widely cited rule of thumb that English
text runs about **4 characters per token** — transparent and dependency-free. Cost is
then computed exactly from a per-model price table (USD per 1M input/output tokens).
The tool is explicit that the token count is an estimate and the cost is exact given
that count.

Two modes:
- `--text "..."` — size a single string.
- `--file data.jsonl --fields prompt,response` — size a dataset, reporting total
  tokens, average per row, and estimated input cost.

## How to run

```bash
python -m pytest

python token_counter.py --text "hello world" --model haiku
# tokens (est): 3
# input cost @ haiku: $0.000002

python token_counter.py --file sample_data/dataset.jsonl --fields prompt,response --model sonnet
# { "n_rows": 3, "input_tokens": ..., "estimated_input_cost_usd": ... }
```

## What this demonstrates

- A practical **budgeting tool** for real model workflows, with a clear estimate/exact
  boundary.
- A transparent tokenization heuristic and **exact, independently verifiable cost math**
  (1M tokens at $3/M = $3.00, checked in the tests).
- A clean CLI with mutually exclusive modes and a per-model price table, no dependencies.
