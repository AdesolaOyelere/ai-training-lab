# Summary Quality Rubric

> A complete annotation handbook for rating summary quality — dimensions, a 1–4
> scale, a decision rule, and edge cases — backed by executable rubric code that
> reproduces every gold calibration label, so the guideline and the code can't drift.

**Category:** `08-annotation-guidelines` · **Skills:** annotation guideline design, rubric design, calibration, Python

## Problem

Annotation quality lives or dies on the guideline. A vague rubric produces
inconsistent labels; a good one defines each dimension, its scale, how dimensions
combine into a decision, and — crucially — how to handle the edge cases annotators
actually hit. And a guideline written only as prose tends to drift from how the data
is really scored. This project pairs a real handbook with code that enforces it.

## Approach

- **[`HANDBOOK.md`](HANDBOOK.md)** — the guideline: four dimensions (coverage,
  faithfulness, conciseness, fluency), a 1–4 scale for each, the weighted decision
  rule, and a worked edge-case section (fluent-but-fabricated, faithful-but-thin,
  borderline all-3s, opinion in the source).
- **`rubric.py`** — the same rules as code: validation, weighted scoring, a hard
  **faithfulness gate** (a hallucinated summary rejects regardless of other scores),
  and a **coverage requirement** for acceptance.
- **`gold_examples.json`** — calibration examples with correct decisions and reasoning.
  `score_against_gold()` verifies the documented rules reproduce every gold label, so
  the handbook and the implementation are provably in sync.

## How to run

```bash
python -m pytest       # includes the guideline-vs-gold consistency check
python run.py          # verify the rules reproduce every gold calibration label
```

## Sample output

```
gold examples: 7
rule/label agreement: 1.000
all gold labels reproduced by the documented rules
```

The interesting cases are the ones that separate a good rubric from a naive one: a
fluent summary that invents a fact is **rejected** (faithfulness gate), and a faithful,
readable summary that misses a key point is a **revise**, not an accept (coverage
requirement) — both encoded and tested.

## What this demonstrates

- Writing a **real annotation guideline**: scales, a decision rule, and the edge cases
  that drive annotator disagreement.
- Turning a rubric into **executable, testable** logic with a calibration set.
- A consistency check that keeps documentation and implementation from diverging.
