# SFT Data Prep

> Turn a messy raw dataset into a clean, deduplicated SFT set in `messages` format —
> and get a per-stage report showing exactly why each dropped row was dropped.

**Category:** `07-finetuning` · **Skills:** data engineering, SFT data cleaning, Python

## Problem

Raw supervised-fine-tuning data is never clean: blank fields, ragged whitespace, exact
duplicates, placeholder rows (`TODO`, `N/A`), and answers that are empty or absurdly
long. Training on that hurts. You want a documented, reproducible cleaning pass — and,
just as importantly, a record of what it removed so the dataset's provenance is clear.

## Approach

`prepare.py` runs an ordered pipeline and tallies every drop:

1. missing `prompt`/`response` field
2. empty after whitespace normalization
3. placeholder text (`TODO`, `TBD`, `N/A`, `lorem ipsum`, …)
4. too short / too long (configurable character bounds)
5. exact duplicate (case-insensitive, after normalization)

Survivors are emitted in OpenAI `messages` format (with an optional `system` turn
preserved), and the report gives per-stage counts plus a keep rate.

## How to run

```bash
python -m pytest
python run.py                 # writes results/cleaned.jsonl + report
python run.py my_raw.jsonl
```

## Sample output

12 raw rows in, from `results/report.md`:

| Stage | Count |
|---|---|
| input | 12 |
| dropped_missing_field | 1 |
| dropped_empty | 3 |
| dropped_placeholder | 2 |
| dropped_duplicate | 1 |
| **kept** | **5** |
| keep_rate | 0.417 |

Every drop is attributable to a specific rule, which is exactly the provenance you'd
publish alongside a cleaned dataset.

## What this demonstrates

- Real **data-engineering for fine-tuning**: an ordered, documented cleaning pipeline.
- Output in the exact `messages` schema trainers expect, system prompts preserved.
- Transparent, auditable filtering with per-stage accounting, fully tested.
