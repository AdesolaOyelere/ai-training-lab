# Self-Critique Refinement Loop

> The draft → critique → revise pattern, made deterministic so you can watch the
> violation count fall to zero — including the subtle convergence bug that makes naive
> refinement loops oscillate forever.

**Category:** `05-synthetic-data` · **Skills:** synthetic data, self-refinement, iterative improvement, Python

## Problem

Self-refinement — generate a draft, critique it, revise, repeat — is a common way to
raise the quality of synthetic data. The structure looks simple, but it has a real
failure mode: if two constraints fight each other, a careless reviser can undo one fix
while making another, and the loop never converges.

## Approach

`refine.py` runs the loop deterministically:

- **critique** checks a draft against a spec (max words, must-end-with-period, no double
  spaces, required keywords, no trailing space) and lists violations.
- **revise** applies a targeted fix per violation. The important detail: the length trim
  is **keyword-aware** — it reserves room for required keywords and only trims
  non-keyword words, so adding a keyword and enforcing a word limit don't fight.
- the loop repeats until the critic is satisfied or a max-iteration cap is hit, and
  records the trajectory of `(text, violations)` at each step.

## How to run

```bash
python -m pytest
python run.py     # refine a deliberately flawed draft, print the trajectory
```

## Sample output

```
converged: True in 2 iteration(s)
  iter 0: 4 violation(s) ['too_long', 'no_end_period', 'double_spaces', 'missing:safety']
  iter 1: 0 violation(s) []
final: 'This guide explains how the system works in considerable detail across safety.'
```

The draft starts with four simultaneous violations and the loop drives them to zero in
one revision. A regression test pins the trickiest case — adding the required keyword
`safety` under a tight word limit — which a naive reviser would oscillate on forever.

## What this demonstrates

- The **self-refinement loop** implemented with a real convergence guarantee, not just
  hope.
- Awareness of the **oscillation failure mode** when constraints interact, and a fix for it.
- A recorded trajectory and an iteration cap, with the convergence behavior unit-tested.
