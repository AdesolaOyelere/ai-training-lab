# Factual QA with Citations

> A QA dataset where every answer must cite the source sentences that support it — plus
> a verifier that checks the citations are real *and* that they actually back the answer.

**Category:** `09-reasoning-datasets` · **Skills:** reasoning-dataset design, attribution, RAG faithfulness, Python

## Problem

For factual and RAG-style QA, a trustworthy answer isn't just correct — it's
*attributable*: it points to the source sentences that support it. Two failure modes hide
here: citing a real but **unrelated** sentence, and making a claim the citation doesn't
actually support (an uncited claim). Grading only the final answer misses both.

## Approach

Each item is `{question, source: [{id, text}], answer, citations: [id]}`. `verify.py`
checks two things:

1. **valid citations** — every cited id points to a real source sentence (bad ids are
   flagged),
2. **support** — the fraction of the answer's content words that appear in the *cited*
   sentences; an answer is `grounded` only when it has a valid citation and support
   clears a threshold.

`evaluate()` reports the grounded rate, mean support, and how many items had invalid
citations.

## How to run

```bash
python -m pytest
python run.py     # verify dataset.jsonl
```

## Sample output

5 items chosen to exercise each failure mode (`results/results.json`):

```
grounded rate: 0.4   mean support: 0.4   items with invalid citations: 1
  c1: grounded=True  support=1.0            # correct answer, correct citation
  c2: grounded=True  support=1.0
  c3: grounded=False support=0.0            # right answer, cites the WRONG sentence
  c4: grounded=False support=0.0            # uncited claim (temples/gold not in source)
  c5: grounded=False support=0.0 invalid=['s9']   # citation id does not exist
```

The verifier separates the three failure modes cleanly: a misattributed answer, an
unsupported claim, and a dangling citation are each caught for a different reason —
which is exactly what an attribution check needs to do.

## What this demonstrates

- Building a **citation-grounded QA dataset** with a real attribution verifier.
- Checking **groundedness** (answer supported by *what it cited*), not just correctness.
- Distinct handling of invalid, misattributed, and unsupported citations, fully tested.
