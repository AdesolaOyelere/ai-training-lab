# Tool-Calling Eval Harness

> Score an agent's tool calls the way you actually need to: is the call
> schema-valid, did it pick the right tool, and are the arguments correct — reported
> as separate, trackable rates.

**Category:** `06-agentic-tasks` · **Skills:** agentic evaluation, tool use, schema validation, Python

## Problem

When an agent calls tools, "did it work?" is not one number. It can pick the right
tool with wrong arguments, produce a call that doesn't even fit the tool's schema, or
choose the wrong tool entirely. Collapsing all of that into a single pass/fail hides
exactly the information you need to improve the agent, so the harness measures each
axis on its own.

## Approach

- **Tool catalog** (`harness.py`) — each tool declares required/optional params and
  their types.
- **`validate_call`** — checks a `{tool, args}` call against the catalog: unknown
  tool, missing required args, unexpected args, and wrong types (with `True` correctly
  *not* accepted as an int).
- **`score_task`** — separates **tool selection** from **argument correctness**, so a
  right-tool/wrong-args call is scored differently from a wrong-tool call.
- **`run_harness`** — aggregates into valid-call rate, tool-selection accuracy,
  argument match given the correct tool, and full pass rate. The agent sits behind a
  swappable seam (a deterministic mock here; drop in a live model the same way).

## How to run

```bash
python -m pytest
python run.py     # writes results/results.json + results.md
```

## Sample output

8 tasks with a deliberately imperfect agent (`results/results.md`):

| Metric | Value |
|---|---|
| Valid-call rate | 0.750 |
| Tool-selection accuracy | 0.875 |
| Arg match (given correct tool) | 0.571 |
| Full pass rate | 0.500 |

The breakdown is the point: the agent chose the right tool 7/8 times but only got the
arguments right on 4 of those, and two calls were not even schema-valid (a missing
argument and a string where an int was required). One number would have hidden all of
that.

## What this demonstrates

- Designing an **agentic eval** that isolates tool selection from argument accuracy.
- Real schema validation of tool calls, including the `bool`-is-not-`int` trap.
- A clean agent seam so the same harness scores a mock or a live model unchanged.
