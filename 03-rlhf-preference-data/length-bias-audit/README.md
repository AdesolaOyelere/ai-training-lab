# Length-Bias Audit

> Check a preference dataset for the most common reward-model shortcut — preferring
> the longer answer — before it becomes a trained-in artifact.

**Category:** `03-rlhf-preference-data` · **Skills:** RLHF data quality, statistics, Python

## Problem

Reward models trained on human preferences frequently learn to equate "longer" with
"better", which produces verbose, padded model outputs. The bias usually originates in
the data: annotators lean toward the longer response regardless of quality. You want to
detect and quantify that signal in a chosen/rejected set so you can length-balance it
or add a penalty before training.

## Approach

`audit.py` computes three complementary signals over a set of `{chosen, rejected}`
pairs:

- **longer_chosen_rate** — fraction of pairs where the chosen answer is longer (0.5 is
  neutral).
- **mean_length_delta** — average token-length gap between chosen and rejected.
- **point_biserial** — the correlation between "was chosen" (1/0) and response length
  across all responses; 0 means length carries no information about the choice.

It then emits a plain-language verdict with a suggested guard.

## How to run

```bash
python -m pytest
python run.py                 # audit dataset.jsonl
python run.py my_pairs.jsonl
```

## Sample output

8 pairs constructed with a strong length preference (`results/results.json`):

```
longer_chosen_rate: 0.75
mean_length_delta: 10.25
point_biserial: 0.5512
verdict: strong length bias — length-balance the data or add a length penalty
```

The three metrics agree: three quarters of pairs pick the longer answer, the chosen
answers are ~10 tokens longer on average, and length correlates 0.55 with being chosen
— well past the "strong" threshold, so the audit recommends acting before training.

## What this demonstrates

- Awareness of a **real RLHF failure mode** and how it enters through the data.
- A statistically grounded audit (point-biserial correlation) with actionable thresholds.
- Clean, dependency-free analysis with tests covering the biased and balanced extremes.
