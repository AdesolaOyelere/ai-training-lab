# Inter-Annotator Agreement

> Measure how much your labelers actually agree — beyond what chance would give —
> with percent agreement, Cohen's kappa, and Fleiss' kappa computed from raw
> annotation rows.

**Category:** `03-rlhf-preference-data` · **Skills:** annotation quality, agreement statistics, Python

## Problem

Preference and labeling data is only as good as the people producing it. Before you
train on it, you want to know whether annotators are consistent. Raw percent
agreement is misleading because two people can agree a lot just by chance when one
label dominates. Cohen's and Fleiss' kappa correct for that, and they're the metrics
a data-quality reviewer is expected to know cold.

## Approach

`agreement.py` takes a flat list of rows — `{"item", "annotator", "label"}` — and
computes:

- **percent agreement** for a pair of annotators,
- **Cohen's kappa** for two annotators (observed vs chance agreement),
- **Fleiss' kappa** for any number of annotators with a constant number of raters
  per item,
- a full `analyze()` report: mean pairwise percent agreement, mean pairwise Cohen's
  kappa, and Fleiss' kappa across the whole set.

The kappa implementations are validated against known values — the two-rater case is
hand-computable, and the Fleiss case is checked against the standard worked example
(κ ≈ 0.210), so the numbers are trustworthy, not just plausible.

## How to run

```bash
python -m pytest                         # validates the metrics against known values
python run.py                            # report over sample_data/annotations.jsonl
python run.py path/to/annotations.jsonl
```

## Sample output

12 preference items, 3 annotators, labels `A / B / tie` (`results/report.md`):

| Metric | Value |
|---|---|
| Mean percent agreement | 0.611 |
| Mean pairwise Cohen's kappa | 0.404 |
| Fleiss' kappa | 0.399 |

Percent agreement (61%) looks decent, but the kappas (~0.40) tell the real story:
only *moderate* agreement once chance is removed — exactly the gap these metrics
exist to expose.

## What this demonstrates

- Knowing the **right** annotation-quality metrics and why raw agreement misleads.
- Correct, textbook-validated implementations of Cohen's and Fleiss' kappa.
- Turning messy annotation rows into a clean, decision-ready quality report.
