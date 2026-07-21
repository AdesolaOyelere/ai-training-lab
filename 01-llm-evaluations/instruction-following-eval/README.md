# Instruction-Following Eval

> Grade model outputs against constraints that can be checked exactly — word
> counts, required keywords, valid JSON, line structure — so the score is
> objective and cheap, with no LLM-as-judge in the loop.

**Category:** `01-llm-evaluations` · **Skills:** eval design, verifiable constraints, benchmark building, Python

## Problem

"Did the model follow the instructions?" is one of the most common things an AI
trainer has to measure, and doing it with another model as a judge is slow,
expensive, and noisy. A large class of instructions are actually *verifiable*:
"exactly 3 lines", "under 15 words", "must be valid JSON with these keys", "start
with `Remember:`". Those can be graded by code, exactly and for free.

This project is a small benchmark harness in that style. Each item is a prompt
plus a list of machine-checkable constraints; the grader reports the fraction of
constraints satisfied and a stricter perfect rate.

## Approach

- **13 constraint checkers** (`eval.py`) — word-count bounds, required / forbidden
  substrings and whole words, `starts_with` / `ends_with`, valid JSON, required
  JSON keys, exact line count, max sentences, regex match, and a no-markdown
  check. Each is a pure function of the output text.
- **Data model** — an `EvalItem` is a prompt plus typed `Constraint`s, loaded from
  `dataset.jsonl`. Scoring is deterministic.
- **Swappable providers** (`providers.py`) — a `mock_provider` replays committed
  responses so the eval is reproducible offline and in CI; an `anthropic_provider`
  runs a live model when `ANTHROPIC_API_KEY` is set. The eval logic never changes
  between them.

## How to run

```bash
python -m pytest          # deterministic core + a full pinned run; no API key needed
python run.py --report    # writes results/results.json and results/results.md
python run.py --live      # grade a live Anthropic model instead of the mock
```

## Sample output

From `results/results.md` (mock provider over the committed dataset):

- Items: **8**
- Mean constraint satisfaction: **0.875**
- Perfect rate (all constraints pass): **0.750**

Two items fail exactly one constraint each — an over-long bullet list (6 lines
where 5 were required) and a note that omits its final period — which is the
harness doing its job: catching partial instruction-following that a quick read
would miss.

## What this demonstrates

- Designing an **objective, reproducible eval** instead of reaching for a judge model.
- Turning fuzzy "follow the instructions" requirements into **verifiable checks**.
- Clean, testable Python: a checker registry, a typed data model, and a provider
  seam that keeps the grader independent of any specific model.
