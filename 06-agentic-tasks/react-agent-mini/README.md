# ReAct Agent (Mini)

> A minimal but real ReAct loop — thought → action → observation → answer — over safe
> mock tools, with the full trace recorded and proper guardrails. The reasoning policy
> is pluggable, so a deterministic stand-in or a live model uses the same interface.

**Category:** `06-agentic-tasks` · **Skills:** agent design, the ReAct loop, tool use, Python

## Problem

The ReAct pattern (reason + act) underpins most tool-using agents, but the interesting
engineering is the *loop and its guardrails*, not the model: a clean tool registry,
observations fed back into the next decision, a recorded trace you can inspect or
score, and hard stops so a misbehaving policy can't loop forever or call a tool that
doesn't exist.

## Approach

`agent.py` provides:

- **Three safe tools** — `calculator` (arithmetic via a restricted AST evaluator, *not*
  `eval`), `lookup` (a tiny knowledge base), and `wordcount`.
- **`run(question, policy, max_steps)`** — the loop: it asks the policy for the next
  move, executes tool actions, appends each `Step` (thought/action/input/observation)
  to a `Trace`, and stops on an answer, an unknown tool, or the step cap.
- **A pluggable `Policy`** — the default `rule_based_policy` is a deterministic
  stand-in for a model (so the whole thing runs offline and in tests); a real model
  policy implements the same `(question, trace) -> move` signature.

## How to run

```bash
python -m pytest
python run.py     # runs 5 questions and writes results/traces.json
```

## Sample output

```
Q: What is 12 * (3 + 4)?
  -> 84  (1 step, answered)          # used the calculator tool
Q: What is the capital of France?
  -> Paris  (1 step, answered)       # used the lookup tool
Q: How many words are here: the quick brown fox jumps
  -> 5  (1 step, answered)           # used the wordcount tool
Q: What is the meaning of life?
  -> I don't know  (0 steps)         # no tool applies, answers directly
```

Each answer comes with a full trace showing which tool was called and what it returned.

## What this demonstrates

- The **ReAct loop** built properly: tool registry, observation feedback, trace, and
  guardrails (max-steps and unknown-tool stops), all tested.
- A **safe calculator** (AST-restricted, arbitrary code rejected) rather than `eval`.
- A clean policy seam so the same loop runs on a rule-based stand-in or a live model.
