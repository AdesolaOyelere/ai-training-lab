# Self-Consistency Voting

> Sample several answers and take the majority (self-consistency), then *measure* how
> much that beats a single sample — with answer normalization and a deterministic
> tie-break, and an honest case where voting still fails.

**Category:** `02-prompt-engineering` · **Skills:** prompt engineering, self-consistency, evaluation, Python

## Problem

Self-consistency prompting samples multiple reasoning chains and votes on the answer,
which is more reliable than any single sample — *when* the correct answer is the most
common one. The technique is widely cited but the benefit should be quantified on your
data, not assumed, and its limits shown honestly.

## Approach

`voting.py`:

- **normalizes** answers before counting, so "1,200", "1200", and "$1200" vote together,
- takes the **majority vote** with a deterministic tie-break (earliest sample among the
  tied),
- reports **majority-vote accuracy** against two single-sample baselines: the first
  sample, and the expected accuracy of drawing one sample at random.

## How to run

```bash
python -m pytest
python run.py     # compares single-sample vs majority vote over dataset.jsonl
```

## Sample output

8 questions, 5 sampled answers each (`results/results.json`):

```
single-sample accuracy (first):    0.375
single-sample accuracy (expected): 0.600
majority-vote accuracy:            0.875
```

Voting lifts accuracy from ~0.38–0.60 to 0.875 — but not to 1.0: one question
(`gold = 3`) has the model answering "4" three times out of five, so the majority is
confidently wrong. That honest failure is the whole point — self-consistency amplifies
whatever the model believes most often, right or wrong.

## What this demonstrates

- **Self-consistency** implemented and, more importantly, *measured* against baselines.
- Practical answer normalization and a deterministic tie-break.
- An honest account of when voting helps and when it doesn't, with both cases tested.
