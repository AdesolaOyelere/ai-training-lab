# Logic Puzzles with Checkers

> Logic puzzles that ship with *programmatic checkers* — so a model's solution can be
> graded by whether it satisfies the rules, not by matching a stored answer string.

**Category:** `09-reasoning-datasets` · **Skills:** reasoning dataset design, verifiers, constraint solving, Python

## Problem

A reasoning dataset with only stored answers can't recognize a correct solution phrased
differently, and can't tell you *why* a wrong one is wrong. Pairing each puzzle with a
checker — a function that validates any candidate against the rules — makes grading
robust and lets you accept every valid answer. It's the same "verifier over answer key"
idea that makes reasoning evals trustworthy.

## Approach

`puzzles.py` defines three puzzles, each with a **checker** (validates a candidate) and
a **solver** (brute-forces the solution space to confirm the answer is unique):

- **seating** — order four people under position constraints (left-of, not-at-ends,
  immediately-right-of).
- **numbers** — place 1–4 in cells so a sum equation, an inequality, and a parity rule
  all hold.
- **knights_knaves** — the classic "we are both knaves" statement; knights tell the
  truth, knaves lie.

Each checker enforces every stated constraint, so it can grade a proposed solution by
correctness. Each puzzle is verified to have exactly one solution.

## How to run

```bash
python -m pytest
python run.py     # solves each puzzle and confirms uniqueness + checker agreement
```

## Sample output

```
seating: solution=['A', 'D', 'C', 'B'] unique=True confirmed=True
numbers: solution={'w': 1, 'x': 4, 'y': 2, 'z': 3} unique=True confirmed=True
knights_knaves: solution=(False, True) unique=True confirmed=True   # A is a knave, B a knight
```

Every puzzle has a single solution, and each puzzle's own checker confirms it — the
property that makes the dataset safe to grade against.

## What this demonstrates

- Building a **reasoning dataset with verifiers**, not just answer keys.
- Encoding logic constraints precisely enough to both solve and check.
- Confirming well-posedness (unique solutions) programmatically, fully tested.
