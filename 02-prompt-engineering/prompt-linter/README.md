# Prompt Linter

> Prompt-engineering best practices encoded as checks: point a linter at an
> instruction and get back the anti-patterns it contains plus a 0-100 score.

**Category:** `02-prompt-engineering` · **Skills:** prompt engineering, static analysis, Python

## Problem

Most weak prompts fail for the same handful of reasons: they never say what output
they want, they paste input without delimiters, they ask to be "brief but
comprehensive", they lean on vague quantifiers, or they demand JSON with no example.
These are learnable, checkable patterns — so instead of writing prose about them, this
project turns them into a deterministic linter.

## Approach

`linter.py` runs a set of rules over a prompt, each producing an `Issue` with a
severity:

- `no_output_format` — the prompt never states the desired output shape
- `undelimited_input` — input is referenced but not wrapped in delimiters
- `conflicting_length` — asks for brevity and thoroughness at once
- `vague_quantifier` — "some", "a few", "as needed", "relevant"…
- `unclear_task` — no imperative task verb
- `no_example_for_structure` — JSON/table requested without an example
- `politeness_filler`, `too_long`, `shouting` — lower-severity noise

Severities map to penalties and the prompt gets a score out of 100.

## How to run

```bash
python -m pytest
python run.py                 # lint prompts.jsonl -> results/report.md
python run.py my_prompts.jsonl
```

## Sample output

Six example prompts (`results/report.md`):

| Prompt | Score | Issues |
|---|---|---|
| `p2` (strong classifier) | 100 | — |
| `p5` (structured + example) | 100 | — |
| `p4` (JSON, no example) | 76 | undelimited_input, no_example_for_structure |
| `p3` ("comprehensive but very short") | 38 | no_output_format, undelimited_input, conflicting_length |
| `p1` (filler, vague, no format) | 21 | no_output_format, undelimited_input, vague_quantifier, unclear_task, politeness_filler |

The scores line up with intuition: the two well-formed prompts are clean, and the
weakest one is flagged on five independent axes.

## What this demonstrates

- Concrete **prompt-engineering knowledge**: the specific things that make prompts
  fail, expressed precisely enough to check automatically.
- Clean rule-based static analysis with severities and scoring.
- A tool that could plug into a prompt-review workflow, fully tested and dependency-free.
