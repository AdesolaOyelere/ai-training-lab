# Math Word Problems (Graded)

> A small reasoning dataset paired with a robust final-answer checker — the piece
> that actually makes a reasoning dataset usable, because exact string match grades
> "1,200" and "$1200" as different answers.

**Category:** `09-reasoning-datasets` · **Skills:** dataset design, answer checking, Python

## Problem

Building a reasoning dataset is half the job; grading answers fairly is the other
half. Models return the right answer in many surface forms — `1200`, `1,200`,
`$1,200.00`, `3/8` vs the unreduced `6/16`, `No.` vs `no` — and they often show
intermediate numbers before the final one. A naive grader either wrongly fails
correct answers or wrongly passes an intermediate value.

## Approach

Each item declares an `answer_type` so grading is type-aware (`grader.py`):

- **number** — strips `$` and commas, and reads the answer *after* a final-answer
  marker ("final answer", "the answer is", "=") so an intermediate value doesn't win.
- **fraction** — compares with `fractions.Fraction`, so `3/12` grades equal to `1/4`.
- **text** — normalizes case and punctuation for short labels like yes/no.

`grade_dataset()` scores a whole run and breaks accuracy down by answer type.

## How to run

```bash
python -m pytest
python run.py     # grade model_outputs.jsonl -> results/results.md
```

## Sample output

8 problems, one model run (`results/results.md`):

- Overall accuracy: **0.875**
- By type: number **0.80**, fraction **1.00**, text **1.00**

The single miss (`m7`) is a model that computed the discount correctly mid-reasoning
but stated the wrong final number (25 instead of 30). The grader catches it precisely
because it reads the *stated* final answer rather than the first number it sees —
which is exactly the behavior a trustworthy checker needs.

## What this demonstrates

- Designing a reasoning dataset **together with** the grader that makes it usable.
- Robust answer extraction: numeric normalization, fraction equivalence, final-answer
  detection, and text-label matching.
- Honest, type-broken-down accuracy reporting, fully tested and dependency-free.
