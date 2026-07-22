# Stratified Leakage-Safe Split

> Split a labeled dataset into train/val/test the right way — preserving class balance
> *and* preventing leakage by keeping duplicate examples out of two splits at once.

**Category:** `07-finetuning` · **Skills:** data engineering, train/test splitting, leakage prevention, Python

## Problem

Two quiet mistakes wreck a fine-tuning evaluation:

1. **Unstratified splits** skew the label balance, so test accuracy reflects the split,
   not the model.
2. **Leakage** — the same example (or a duplicate) appears in both train and test — so
   the model is scored partly on data it trained on, inflating results.

A splitter has to avoid both, and be deterministic so results are reproducible.

## Approach

`split.py`:

- **Groups duplicate texts** (normalized) into a single leakage unit so a group can
  never span two splits.
- **Allocates each label's groups** across train/val/test to match the target ratios,
  which preserves class proportions (stratification).
- Is **deterministic** given a seed (a hash-based ordering, no global RNG state).

`report()` returns split sizes, overall vs per-split label proportions, and a
`no_leakage` flag; `check_no_leakage()` verifies no text appears in two splits.

## How to run

```bash
python -m pytest
python run.py     # splits a 22-row dataset (with planted duplicates)
```

## Sample output

```
total 22 -> sizes {'train': 12, 'val': 5, 'test': 5}
overall label props: {'neg': 0.5, 'pos': 0.5}
per-split label props: {'train': {'neg': 0.5, 'pos': 0.5}, 'val': {...}, 'test': {...}}
no leakage: True
```

The dataset is 50/50 and the train split stays exactly 50/50; the two planted duplicate
texts each land wholly within one split, and the leakage check passes.

## What this demonstrates

- **Leakage-aware** splitting (grouping duplicates) — a subtle bug most splitters miss.
- **Stratification** to preserve class balance across splits.
- Deterministic, reproducible data engineering with the invariants (completeness,
  no-leakage, balance, determinism) all unit-tested.
