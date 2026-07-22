# Harmful Request Classifier

> A fast, transparent first-pass triage that routes incoming requests into three risk
> tiers — **allow**, **caution**, **refuse** — with the higher tier always winning,
> scored with accuracy and per-tier recall.

**Category:** `04-red-teaming-safety` · **Skills:** AI safety, risk triage, classification, Python

## Problem

A safety layer needs to triage requests quickly: most are clearly benign, some are
sensitive-but-answerable (medical, legal, financial questions that need care and
disclaimers), and some should be refused outright. Collapsing this into a binary
safe/unsafe loses the middle tier, which is exactly where thoughtful handling matters.

## Approach

`classifier.py` assigns a tier with a strict precedence — **refuse > caution > allow** —
so a request that trips any disallowed pattern is refused even if it also looks
sensitive:

- **refuse** — weapon/explosive synthesis, account hacking, self-harm facilitation,
  malware, financial crime.
- **caution** — medical dosage/symptom questions, legal advice, investment advice,
  mental-health topics.
- **allow** — everything with no risk pattern.

`evaluate()` scores predictions against a labeled set and reports accuracy plus
per-tier recall and a full confusion matrix. It's deliberately interpretable — a
production system would add a model classifier, but the tiers and the evaluation are
the transferable part.

## How to run

```bash
python -m pytest
python run.py     # evaluate dataset.jsonl
```

## Sample output

12 labeled requests (4 per tier):

```
accuracy: 1.0 (12 requests)
per-tier recall: {'allow': 1.0, 'caution': 1.0, 'refuse': 1.0}
```

Perfect tiering **on this labeled set** — including the precedence rule, verified by a
test where a request mentions a medical word *and* a refuse pattern and is correctly
refused rather than merely cautioned.

## What this demonstrates

- **Risk triage** framed as a three-tier problem, not a lossy binary.
- A clear precedence rule (fail-safe: refuse wins) and an honest, measured evaluation.
- Defensive, interpretable classification with a full confusion matrix, fully tested.
