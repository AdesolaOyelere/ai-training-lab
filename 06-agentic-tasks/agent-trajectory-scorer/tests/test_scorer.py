"""Tests for the trajectory scorer: each rubric dimension behaves correctly (success,
efficiency decay, validity on errors, loop penalty), and the aggregate over the three
committed trajectories (clean, wandering, looping-fail) is pinned."""
import json
from pathlib import Path

from scorer import evaluate, score

HERE = Path(__file__).resolve().parent.parent


def test_success_dimension():
    task = {"expected_answer": "84", "optimal_steps": 1}
    good = {"answer": "84", "steps": [{"action": "calc", "input": "12*7", "observation": "84"}]}
    bad = {"answer": "80", "steps": [{"action": "calc", "input": "12*7", "observation": "80"}]}
    assert score(good, task)["success"] == 1.0
    assert score(bad, task)["success"] == 0.0


def test_efficiency_decays_with_extra_steps():
    task = {"expected_answer": "x", "optimal_steps": 1}
    three = {"answer": "x", "steps": [{"action": "a", "input": str(i), "observation": "o"} for i in range(3)]}
    # 2 extra steps -> 1 - 0.25*2 = 0.5
    assert score(three, task)["efficiency"] == 0.5


def test_validity_and_loops():
    task = {"expected_answer": "x", "optimal_steps": 5}
    traj = {
        "answer": "x",
        "steps": [
            {"action": "t", "input": "1", "observation": "error: boom"},
            {"action": "t", "input": "1", "observation": "error: boom"},   # repeat + error
        ],
    }
    r = score(traj, task)
    assert r["validity"] == 0.0        # both steps errored
    assert r["no_loops"] == 0.5        # one repeated (action, input)


def test_aggregate_pins_committed():
    pairs = json.loads((HERE / "trajectories.json").read_text(encoding="utf-8"))
    m = evaluate(pairs)
    per = {r["id"]: r for r in m["per_trajectory"]}
    assert per["clean"]["overall"] == 1.0
    assert per["wandering"]["success"] == 1.0 and per["wandering"]["efficiency"] == 0.5
    assert per["looping_fail"]["overall"] < 0.3
    committed = json.loads((HERE / "results" / "results.json").read_text(encoding="utf-8"))
    assert committed == m
