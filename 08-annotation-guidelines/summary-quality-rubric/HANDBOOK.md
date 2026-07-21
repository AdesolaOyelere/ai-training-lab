# Annotation Handbook — Summary Quality

This is the guideline an annotator follows to rate the quality of a machine- or
human-written summary against its source text. It defines the dimensions, the 1–4
scale for each, how to combine them into a decision, and the tricky cases. The rules
here are mirrored exactly by `rubric.py`, so the guideline is executable, not just
advisory.

## What you are rating

You are given a **source text** and a **summary** of it. Rate the summary only — not
the source, and not whether you personally agree with the source.

## Dimensions and the 1–4 scale

Rate each dimension independently.

### Coverage — are the key points present?
- **4** — captures all the main points; nothing important is missing.
- **3** — captures most main points; a minor point is missing.
- **2** — misses at least one **key** point.
- **1** — misses most of what matters; not representative of the source.

### Faithfulness — is everything supported by the source?
- **4** — every claim is directly supported by the source.
- **3** — supported, with at most a harmless imprecision.
- **2** — contains a claim that overstates or distorts the source.
- **1** — invents facts not in the source (hallucination).

### Conciseness — free of redundancy?
- **4** — tight; no filler or repetition.
- **3** — slightly wordy but acceptable.
- **2** — noticeably padded or repetitive.
- **1** — mostly filler relative to its information.

### Fluency — grammatical and readable?
- **4** — clean, natural prose.
- **3** — minor errors that don't impede reading.
- **2** — errors that slow the reader.
- **1** — hard to read.

## From scores to a decision

The overall score is a weighted average — coverage and faithfulness matter most:

| Dimension | Weight |
|---|---|
| Coverage | 0.35 |
| Faithfulness | 0.35 |
| Conciseness | 0.15 |
| Fluency | 0.15 |

Then apply, in order:

1. **Faithfulness gate.** If faithfulness is **1**, the decision is **reject** — a
   hallucinated summary is unusable no matter how fluent. This gate is absolute.
2. **Accept.** Faithfulness ≥ 3 **and** coverage ≥ 3 **and** weighted score ≥ 3.0.
   (A summary that is faithful but misses key points is *not* accepted — it is revised.)
3. **Revise.** Weighted score ≥ 2.0 and not accepted.
4. **Reject.** Everything else.

## Edge cases and how to handle them

- **Fluent but fabricated.** High fluency/conciseness cannot rescue a summary that
  invents a fact. Score faithfulness 1 and it rejects. (See gold example `g4`.)
- **Faithful but thin.** A summary that is accurate and readable but omits a key point
  is a **revise**, not an accept — completeness is a requirement. (See `g7`.)
- **Borderline all-3s.** A summary that is a solid 3 on every dimension lands exactly
  at the accept threshold; treat it as **accept**. (See `g6`.)
- **Opinion in the source.** If the source states an opinion, faithfully reporting
  that opinion is faithful (4). Do not penalize the summary for the source's stance.
- **Length is not conciseness.** A short summary that drops key points is a coverage
  problem, not a conciseness virtue.

## Calibration

`gold_examples.json` holds worked examples with their correct decisions and the
reasoning. New annotators should score these blind and compare; `rubric.py`'s
`score_against_gold()` verifies that the documented rules reproduce every gold label,
so the handbook and the code can never silently drift apart.
