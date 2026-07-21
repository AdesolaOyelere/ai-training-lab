# PII Leak Detector

> Find and redact personally identifiable information — emails, phone numbers, SSNs,
> credit cards (validated with the Luhn checksum), and IP addresses — as a defensive
> utility for scrubbing datasets and screening model outputs.

**Category:** `04-red-teaming-safety` · **Skills:** AI safety, PII detection, redaction, Python

## Problem

Training data and model outputs can leak PII, which is both a privacy risk and a
compliance problem. Before you ship a dataset or surface a model response, you want to
detect PII and be able to redact it — and to *measure* how well the detector does, so
you know what it misses.

## Approach

`pii.py` matches five PII types with transparent patterns and two validity checks that
cut false positives:

- **Luhn checksum** for credit-card numbers, so a random 16-digit string isn't flagged
  as a card.
- **Octet-range check** for IPv4, so `999.999.999.999` is rejected.

`find_pii()` returns typed spans with positions and de-overlaps colliding matches;
`redact()` masks every span; `evaluate()` scores detection on a labeled set with
precision / recall / F1.

## How to run

```bash
python -m pytest
python run.py     # evaluate + a redaction example
```

## Sample output

```
precision 1.0  recall 1.0  f1 1.0
by type: {'email': 2, 'phone': 2, 'ssn': 1, 'credit_card': 1, 'ipv4': 1}
redaction: Contact [REDACTED] or [REDACTED].
```

Precision and recall are perfect **on this curated 11-example set** — the point of the
labeled eval is to make that claim measurable rather than assumed. The Luhn and
octet-range checks are what keep precision high: they reject look-alike numbers that a
naive regex would over-flag.

## What this demonstrates

- A **defensive privacy tool**: detect and redact PII, not exfiltrate it.
- Reducing false positives with real validation (Luhn, IP octet ranges), not just regex.
- Span-accurate redaction and an honest, measured evaluation, fully tested and dependency-free.
