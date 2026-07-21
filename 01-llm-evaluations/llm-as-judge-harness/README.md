# LLM-as-Judge Harness

> Use a model to pick the better of two responses — but control for the judge's
> position bias by judging each pair in both orders and only counting a win when the
> verdict is consistent. Reports win rates *and* a measured position-bias rate.

**Category:** `01-llm-evaluations` · **Skills:** evaluation, LLM-as-judge, bias control, Python

## Problem

Pairwise "which answer is better?" judging with an LLM is everywhere, and it has a
well-documented failure mode: judges tend to prefer whichever response appears first,
regardless of content. If you don't control for this, your win rates are partly
measuring presentation order, not quality.

## Approach

The harness implements the standard debiasing protocol:

1. Judge the pair with answer A shown first.
2. Judge it again with the order **swapped**.
3. Count a win for a model only if the judge favors it **both** times. If the verdict
   flips when the order changes, that's position bias — the pair is scored a **tie**
   and counted toward a reported `position_bias_rate`.

`run_judgements()` aggregates into A/B win rates, tie rate, and the position-bias rate,
so you can see both the outcome and how trustworthy the judge was. The judge is a
swappable `Callable`; a deterministic mock drives the committed results and a real
model drops in unchanged.

## How to run

```bash
python -m pytest
python run.py     # writes results/results.json + results.md
```

## Sample output

7 pairs, with two constructed so the (mock) judge always picks the first answer
(`results/results.md`):

| Metric | Value |
|---|---|
| Model-A win rate | 0.429 |
| Model-B win rate | 0.143 |
| Tie rate | 0.429 |
| **Position-bias rate** | **0.286** |

The two order-sensitive pairs are correctly caught: each flips its verdict when the
order is swapped, so instead of handing model A an undeserved win, the harness records
them as ties and surfaces a 28.6% position-bias rate — the number you'd want to see
before trusting the judge.

## What this demonstrates

- Knowing a **real evaluation pitfall** (position bias) and the standard method to
  control it.
- Aggregating judgments into decision-ready metrics *including* a bias diagnostic.
- A clean judge seam so the same protocol runs on a mock or a live model.
