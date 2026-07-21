# JSON Schema Adherence Eval

> Measure how reliably a model returns JSON in the shape you asked for — and, when it
> fails, *why* — with a conformance rate and a failure breakdown by reason.

**Category:** `01-llm-evaluations` · **Skills:** evaluation, structured output, schema validation, Python

## Problem

Structured-output tasks depend on the model returning JSON in a specific shape, and a
single conformance number ("80% valid") hides the information you actually need. Is the
model emitting prose around the JSON? Getting a type wrong? Dropping a required field?
Using an out-of-range enum value? Each points to a different prompt fix.

## Approach

`schema_eval.py` checks each output against a small schema spec (required keys, types,
enums) and classifies failures into five modes:

- `invalid_json` — not parseable
- `not_an_object` — valid JSON but not an object
- `missing:<field>` — a required field is absent
- `type:<field>` — a field has the wrong type (`bool` correctly not counting as a number)
- `enum:<field>` — a value outside the allowed set

`evaluate()` reports the conformance rate and a tally of failure reasons. Extra fields
are allowed by design — the schema specifies what must be present, not what's forbidden.

## How to run

```bash
python -m pytest
python run.py     # evaluate dataset.jsonl against schema.json
```

## Sample output

8 outputs against a sentiment schema (`results/results.json`):

```
conformance rate: 0.5 (4/8)
failure reasons: {'enum': 1, 'invalid_json': 1, 'missing': 1, 'type': 1}
```

The breakdown is the value: the four failures are one of each kind — prose wrapped
around the JSON, a string where a number was required, a missing `sentiment`, and an
out-of-range enum — so you can see exactly which behaviors to target, not just that
half failed.

## What this demonstrates

- A **structured-output eval** that diagnoses failure modes, not just a pass rate.
- Careful validation semantics (extra fields allowed, `bool` is not a number).
- Clean, dependency-free checking with a committed, reproducible result.
