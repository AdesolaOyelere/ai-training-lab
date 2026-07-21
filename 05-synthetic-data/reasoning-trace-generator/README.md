# Reasoning-Trace Generator

> Generate step-by-step reasoning traces, then keep only the ones an *independent*
> reference can verify — rejection sampling to turn noisy generations into a clean,
> trustworthy training set.

**Category:** `05-synthetic-data` · **Skills:** synthetic data, rejection sampling, verification, Python

## Problem

Synthetic reasoning data is only useful if the answers are actually right. Whether
traces come from a model or a template, a real pipeline has to *filter* — drop
duplicates, drop malformed traces, and above all drop traces whose final answer is
wrong. This project is a compact, fully verifiable version of that pipeline.

## Approach

- **Generate** (`pipeline.py`) — four templated problem types (arithmetic word
  problems, percentage discounts, unit conversions, GCD), each emitting a question,
  numbered reasoning steps, the parameters, and an answer. A tunable `flaw_rate`
  corrupts some answers on purpose, standing in for imperfect real generations.
- **Verify independently** — `expected_answer()` is a *separate* reference
  implementation that recomputes the answer from the stored parameters. The
  generator is never trusted; a trace is kept only if its answer matches the
  reference. This is the same idea as verifying model outputs with a checker instead
  of a judge.
- **Filter** — remove duplicate questions and traces below a minimum step count,
  then keep the verified remainder. Everything is seeded, so runs are reproducible.

## How to run

```bash
python -m pytest              # deterministic; verifies the verifier itself
python run.py                 # writes results/accepted.jsonl + report
python run.py --n 500 --seed 3 --flaw-rate 0.2
```

## Sample output

Default run (`n=200, seed=7, flaw_rate=0.15`), from `results/report.md`:

| Stage | Count |
|---|---|
| Generated | 200 |
| Removed as duplicates | 10 |
| Rejected (wrong answer) | 41 |
| **Accepted** | **149** |
| Acceptance rate | 74.5% |

Every one of the 149 accepted traces has an answer confirmed by the independent
reference, and no two share the same question.

## What this demonstrates

- **Rejection sampling** for data quality: generate broadly, then keep only what
  passes an independent check.
- Separating the **generator from the verifier** so the filter can't rubber-stamp
  its own mistakes — a core habit in building trustworthy training data.
- Deterministic, seeded pipelines with tests that prove the verifier catches wrong
  answers rather than assuming it does.
