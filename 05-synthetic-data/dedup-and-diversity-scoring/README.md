# Dedup & Diversity Scoring

> Remove near-duplicate examples from a dataset and measure how diverse what's left
> actually is — with transparent character n-gram Jaccard similarity, no embeddings
> and no dependencies.

**Category:** `05-synthetic-data` · **Skills:** data quality, deduplication, diversity metrics, Python

## Problem

Synthetic and scraped datasets accumulate near-duplicates: the same instruction
reworded ("sum of two numbers" vs "sum of two integers"), the same answer template
repeated. Exact-match dedup misses these, and training on them wastes budget and skews
the distribution. You want to (1) catch near-duplicates and (2) quantify diversity so
you can tell whether cleaning actually helped.

## Approach

`dedup.py` represents each text as a set of character 4-gram **shingles** and compares
them with **Jaccard similarity** — interpretable and dependency-free:

- **`dedupe`** — greedy pass that keeps an item unless it is ≥ threshold similar to
  something already kept, recording what each removed item duplicated.
- **`diversity_score`** — mean pairwise dissimilarity (1 − Jaccard); 1.0 means every
  item is distinct.
- **`analyze`** — runs dedup and reports diversity before and after.

The default threshold (0.6) sits in the natural gap for this data: near-duplicate
rewordings score 0.6–0.8 while genuinely different items score under 0.1.

## How to run

```bash
python -m pytest
python run.py                  # writes results/results.json + results.md
python run.py --threshold 0.7  # stricter (fewer removed)
```

## Sample output

8 entries with three planted near-duplicates (`results/results.md`):

- Kept **5** of 8; removed **3** (two rewordings of a "sum of two numbers" prompt, one
  "hash table" vs "hash map" pair).
- Diversity **0.886 → 0.982** after dedup.

The removed items each point back to the entry they duplicated, and the diversity jump
quantifies the cleanup — exactly the before/after evidence you'd attach to a dataset
release.

## What this demonstrates

- Practical **data-quality engineering**: near-dup detection without heavyweight tooling.
- A defensible **diversity metric** with a clear before/after story.
- Transparent, testable similarity logic that a reviewer can read top to bottom.
