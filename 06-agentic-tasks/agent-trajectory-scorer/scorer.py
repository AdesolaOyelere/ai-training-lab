"""Score an agent's trajectory against a rubric.

Beyond "did the agent get the right answer", the *quality* of how it got there matters:
was it efficient, did every action succeed, and did it avoid spinning in loops? This
scorer takes a trajectory (the ordered steps an agent took, plus its final answer) and
a task spec (expected answer and an optimal step count) and produces a per-dimension
rubric score with a weighted overall — the kind of trajectory-quality metric you'd
track across agent versions.

A trajectory step is {"action", "input", "observation"}; an observation starting with
"error" marks a failed action.
"""
from __future__ import annotations


def _success(trajectory: dict, task: dict) -> float:
    return 1.0 if str(trajectory.get("answer", "")).strip() == str(task["expected_answer"]).strip() else 0.0


def _efficiency(trajectory: dict, task: dict) -> float:
    """1.0 if within the optimal step count, decaying as extra steps are used."""
    steps = len(trajectory.get("steps", []))
    optimal = max(1, task.get("optimal_steps", 1))
    if steps <= optimal:
        return 1.0
    extra = steps - optimal
    return round(max(0.0, 1.0 - 0.25 * extra), 4)


def _validity(trajectory: dict) -> float:
    """Fraction of steps whose action did not error."""
    steps = trajectory.get("steps", [])
    if not steps:
        return 1.0
    ok = sum(1 for s in steps if not str(s.get("observation", "")).lower().startswith("error"))
    return round(ok / len(steps), 4)


def _no_loops(trajectory: dict) -> float:
    """1.0 if no (action, input) pair repeats; drops with each repeated action."""
    steps = trajectory.get("steps", [])
    if not steps:
        return 1.0
    seen: set[tuple] = set()
    repeats = 0
    for s in steps:
        key = (s.get("action"), s.get("input"))
        if key in seen:
            repeats += 1
        seen.add(key)
    return round(max(0.0, 1.0 - 0.5 * repeats), 4)


RUBRIC_WEIGHTS = {"success": 0.5, "efficiency": 0.2, "validity": 0.2, "no_loops": 0.1}


def score(trajectory: dict, task: dict) -> dict:
    dims = {
        "success": _success(trajectory, task),
        "efficiency": _efficiency(trajectory, task),
        "validity": _validity(trajectory),
        "no_loops": _no_loops(trajectory),
    }
    overall = round(sum(RUBRIC_WEIGHTS[k] * v for k, v in dims.items()), 4)
    return {"id": trajectory.get("id"), **dims, "overall": overall}


def evaluate(pairs: list[dict]) -> dict:
    """pairs: [{trajectory, task}]. Returns per-trajectory scores and means."""
    rows = [score(p["trajectory"], p["task"]) for p in pairs]
    n = len(rows)

    def avg(key: str) -> float:
        return round(sum(r[key] for r in rows) / n, 4) if n else 0.0

    return {
        "n": n,
        "mean_success": avg("success"),
        "mean_efficiency": avg("efficiency"),
        "mean_validity": avg("validity"),
        "mean_no_loops": avg("no_loops"),
        "mean_overall": avg("overall"),
        "per_trajectory": rows,
    }
