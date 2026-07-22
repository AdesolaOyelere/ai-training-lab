# Few-Shot vs Zero-Shot Ablation

> A controlled ablation that measures how accuracy changes as you add few-shot
> exemplars — the exact methodology you'd run against a real model, made honest and
> reproducible on a self-contained task.

**Category:** `02-prompt-engineering` · **Skills:** prompt engineering, ablation design, evaluation, Python

## Problem

"Do examples help, and how many?" is one of the most common prompt-engineering
questions, and answering it properly means an *ablation*: hold the task and test set
fixed, vary only the number of exemplars, and report accuracy per condition. The skill
is the methodology, not any one model.

## Approach

The task is intent classification (greeting / weather / farewell). The "model" is a
nearest-exemplar classifier: given `k` labeled exemplars it labels a test item by its
most similar exemplar (token Jaccard); with **zero** exemplars it can only fall back to
the majority-class prior. `run_ablation()` sweeps `k = 0, 1, 3, 6, 9`, scores the fixed
test set at each, and reports the curve plus whether it's monotonic. Everything is
deterministic, so the result is reproducible and testable.

## How to run

```bash
python -m pytest
python run.py     # prints the accuracy-vs-shots curve, writes results/results.json
```

## Sample output

```
 0 shots -> accuracy 0.333     # prior only
 1 shots -> accuracy 0.333
 3 shots -> accuracy 0.667
 6 shots -> accuracy 1.000
 9 shots -> accuracy 1.000
improvement 0 -> max shots: +0.667
```

Zero-shot can only ever get the prior class right (0.33 across three balanced intents);
once a few exemplars cover all three intents, accuracy climbs to perfect. The curve is
monotonic non-decreasing — the clean shape a well-run ablation should show.

## What this demonstrates

- **Ablation methodology**: isolate one variable (shots), hold the rest fixed, report a curve.
- An honest zero-shot baseline (the prior) rather than a hand-waved number.
- Deterministic, reproducible evaluation with the trend properties asserted in tests.
