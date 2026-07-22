# Annotation Edge-Case Catalog

> The tricky cases every annotator hits on a sentiment task — negation, mixed
> sentiment, sarcasm, comparison, rhetorical questions, conditionals — documented as a
> handbook *and* encoded as a detector that flags which rule applies.

**Category:** `08-annotation-guidelines` · **Skills:** annotation guideline design, edge-case handling, Python

## Problem

Most annotator disagreement comes from a small set of edge cases. A guideline that only
covers the easy cases produces noisy labels. The valuable work is naming those edge
cases, writing the rule for each, and — so the guideline actually gets applied —
surfacing the right rule at annotation time.

## Approach

- **[`EDGE_CASES.md`](EDGE_CASES.md)** — the catalog: six edge cases, each with the
  pattern, an example, and the handling rule (e.g. resolve negation before labeling;
  label comparisons toward the review's subject; treat conditionals with unmet
  premises as disappointment).
- **`catalog.py`** — a detector that flags which edge cases a text triggers, so the
  annotation tool can show the matching guideline. It routes attention; it does not
  assign the label.
- **`gold_examples.json`** — pinned correct routing; the tests assert the detector
  reproduces it, keeping the doc and code in sync.

## How to run

```bash
python -m pytest
python run.py     # routes the gold set and reports edge-case coverage
```

## Sample output

```
flagged 7/8 for review
counts by case: {'comparison': 1, 'conditional': 1, 'contrast_mixed': 2,
                 'negation': 2, 'rhetorical_question': 1, 'sarcasm_cue': 1}
gold mismatches: none
```

Seven of eight examples trip at least one edge case (one clean positive does not), and
the detector matches the gold routing exactly — including the example that triggers
*two* cases at once ("not bad, but slow" → negation + contrast).

## What this demonstrates

- Real **annotation-guideline authorship**: naming edge cases and writing handling rules.
- Making a guideline operational by **routing** inputs to the relevant rule.
- A doc-and-code consistency check (gold routing) so the guideline can't silently drift.
