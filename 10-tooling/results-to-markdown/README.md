# Results to Markdown

> Turn a metrics `results.json` into a clean, shareable Markdown report — scalars as a
> key/value table, nested objects flattened, and lists of records rendered as tables.

**Category:** `10-tooling` · **Skills:** CLI design, reporting, Python

## Problem

Every eval in this lab writes a `results.json`. Pasting those numbers into a readable
report by hand is tedious and error-prone. A small, general renderer that takes any
metrics object and produces tidy Markdown closes that gap and slots into a reporting
step.

## Approach

`to_markdown.py` walks a JSON object and renders:

- **scalars** → a `Metric | Value` table (floats formatted compactly),
- **nested objects** → flattened with dotted keys (`confusion.tp`),
- **a list of uniform dicts** → its own table with a column per key,
- **scalar lists** → a comma-joined value,

with pipe characters escaped so the tables never break.

## How to run

```bash
python -m pytest
python run.py                                   # renders the bundled sample
python to_markdown.py results.json --title "Eval" -o report.md
```

## Sample output

Rendering the bundled `sample_data/results.json`:

```markdown
# Eval Results

| Metric | Value |
|---|---|
| n_items | 8 |
| mean_score | 0.8125 |
| perfect_rate | 0.75 |
| confusion.tp | 6 |
...

## per_item
| id | score | passed |
|---|---|---|
| a1 | 1 | true |
```

## What this demonstrates

- A **general reporting utility** that composes with the rest of the repo's outputs.
- Recursive JSON handling: flattening nested objects and detecting record lists.
- Careful Markdown generation (escaping, compact float formatting), fully tested.
