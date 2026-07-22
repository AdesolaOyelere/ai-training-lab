# Summarization Quality Eval

> Score a summary on three axes that catch the common failure modes — missing points,
> invented facts, and bloat — deterministically, with no judge model in the loop.

**Category:** `01-llm-evaluations` · **Skills:** evaluation, summarization, faithfulness, Python

## Problem

Summarization quality is usually graded with an LLM judge, which is slow and noisy.
When each source ships with its key points, the three axes that matter most can be
scored by code:

- **coverage** — did the summary capture the source's key points?
- **faithfulness** — is everything in the summary supported by the source? (a proxy for
  hallucination)
- **conciseness** — is the summary actually shorter than the source?

## Approach

`summ_eval.py` computes each axis over content words (stop-words removed):

- coverage = fraction of key points whose words are mostly present in the summary,
- faithfulness = fraction of the summary's content words that appear in the source (so
  invented words drag it down),
- conciseness = `1 − (summary_len / source_len)`, with over-long summaries scoring 0.

`evaluate()` reports per-item and mean scores plus a weighted `overall`. These are
transparent proxies, not a final verdict — but they flag the failures a quick read
would miss.

## How to run

```bash
python -m pytest
python run.py     # scores dataset.jsonl
```

## Sample output

4 summaries (`results/results.json`):

```
d1: cov 1.00  faith 0.92  conc 0.21      # complete and faithful
d2: cov 0.40  faith 1.00  conc 0.58      # faithful but MISSES key points
d3: cov 1.00  faith 0.59  conc 0.00      # HALLUCINATES + bloated
d4: cov 1.00  faith 1.00  conc 0.11      # complete and faithful
```

The eval separates the failure modes cleanly: `d2` is penalized for dropping key
points, and `d3` is caught inventing "chocolate sauce and raspberries" (faithfulness
0.59) *and* running longer than its source (conciseness 0.00) — even though its
coverage is perfect. (Conciseness is modest on the good summaries because these sources
are short; the metric measures compression, which these examples don't do heavily.)

## What this demonstrates

- A **multi-axis summarization eval** that isolates coverage, faithfulness, and bloat.
- A transparent **hallucination proxy** (unsupported content words) with no judge model.
- Honest reporting of what the proxies do and don't capture, fully tested.
