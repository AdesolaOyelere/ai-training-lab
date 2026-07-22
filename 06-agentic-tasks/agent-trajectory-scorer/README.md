# Agent Trajectory Scorer

> Score not just whether an agent got the answer, but *how* it got there — efficiency,
> action validity, and loop avoidance — as a weighted rubric you can track across agent
> versions.

**Category:** `06-agentic-tasks` · **Skills:** agentic evaluation, trajectory scoring, rubric design, Python

## Problem

Two agents can both reach the right answer while behaving very differently: one solves
it in a single clean step, the other wanders through redundant searches or spins in a
loop of failing tool calls. A pass/fail on the final answer hides all of that, but it's
exactly what tells you whether an agent is getting better.

## Approach

`scorer.py` scores a trajectory (ordered `{action, input, observation}` steps plus the
final answer) against a task spec (`expected_answer`, `optimal_steps`) on four rubric
dimensions:

- **success** (0.5) — did the final answer match?
- **efficiency** (0.2) — 1.0 within the optimal step count, decaying per extra step.
- **validity** (0.2) — fraction of steps whose action didn't error.
- **no_loops** (0.1) — penalized for each repeated `(action, input)` pair.

`evaluate()` rolls these into per-trajectory and mean scores plus a weighted overall.

## How to run

```bash
python -m pytest
python run.py     # scores the bundled trajectories
```

## Sample output

Three trajectories for the same kind of task (`results/results.json`):

```
clean:        success 1.0  eff 1.0  valid 1.0  no_loops 1.0  -> overall 1.00
wandering:    success 1.0  eff 0.5  valid 1.0  no_loops 1.0  -> overall 0.90
looping_fail: success 0.0  eff 0.75 valid 0.0  no_loops 0.5  -> overall 0.20
```

All three are distinguished by *behavior*, not just the answer: `wandering` reaches the
right answer but takes three steps where one would do, and `looping_fail` repeats a
failing tool call and never succeeds — nuance a single success flag would erase.

## What this demonstrates

- **Trajectory-level agentic evaluation**, not just final-answer pass/fail.
- A weighted rubric capturing efficiency, validity, and looping — the real quality signals.
- Deterministic, transparent scoring with each dimension unit-tested.
