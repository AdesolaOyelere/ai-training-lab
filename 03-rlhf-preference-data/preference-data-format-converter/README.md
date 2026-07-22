# Preference Data Format Converter

> Convert human-preference data between the shapes different RLHF trainers expect —
> pairwise, ranked-list, and binary (KTO-style) — including the ranking→pairwise
> expansion that turns a full ranking into all its better/worse comparisons.

**Category:** `03-rlhf-preference-data` · **Skills:** RLHF data engineering, preference data, Python

## Problem

Preference data is collected and consumed in several formats: pairwise
chosen/rejected, a full ranking of N responses, or per-response binary desirability
(KTO). Trainers want different ones, and hand-converting them — especially expanding a
ranking into pairwise comparisons — is where subtle bugs (an inverted preference, a
dropped pair) creep in.

## Approach

Everything normalizes to a **ranked list of responses, best first**, and each format is
produced from that:

- **pairwise ↔ ranked** — a comparison is a two-element ranking; a ranking of N expands
  to all `C(N,2)` ordered pairs, with the better-ranked response always the `chosen`.
- **binary (KTO)** — the top half of a ranking is labeled desirable (`True`), the bottom
  half undesirable; a single binary row round-trips its own label.

`convert()` maps a whole dataset and reports the offending record index on bad input.

## How to run

```bash
python -m pytest
python run.py     # converts sample_data/ranked.jsonl to pairwise + binary
```

## Sample output

```
2 ranked records -> 4 pairwise comparisons, 5 binary rows
first pairwise: {'prompt': 'Explain gravity simply.',
                 'chosen': 'Gravity pulls objects with mass toward each other.',
                 'rejected': 'Gravity is a force.'}
```

The 3-response ranking expands to 3 ordered pairs and the 2-response ranking to 1 (4
total), and each response becomes a binary row (5 total) — and every generated pair
keeps the better response as `chosen`, verified in the tests.

## What this demonstrates

- Knowledge of the **real preference-data formats** and how they relate.
- The non-trivial **ranking → pairwise** expansion done correctly (order preserved).
- A normalize-then-emit design with indexed error reporting, fully tested.
