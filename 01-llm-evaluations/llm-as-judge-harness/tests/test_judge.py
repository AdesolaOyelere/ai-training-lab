"""Tests for the debiased pairwise judge: a consistent judge yields a real winner,
a position-biased judge is caught and downgraded to a tie, and the aggregate over the
committed dataset (including two deliberately biased pairs) is pinned."""
import json
from pathlib import Path

from judge import Pair, first_position_judge, judge_pair_debiased, run_judgements

HERE = Path(__file__).resolve().parent.parent


def test_consistent_judge_gives_real_winner():
    judge = first_position_judge({})
    pair = Pair("x", "q", "this one is BETTER", "this one is not")
    r = judge_pair_debiased(pair, judge)
    assert r["winner"] == "a"
    assert r["consistent"] and not r["position_bias"]


def test_position_bias_is_detected_and_downgraded():
    # a judge that always picks whichever answer is shown first
    always_first = first_position_judge({"q": "A"})
    pair = Pair("x", "q", "answer one", "answer two")
    r = judge_pair_debiased(pair, always_first)
    assert r["winner"] == "tie"          # flip across orders -> no real winner
    assert r["position_bias"] and not r["consistent"]


def test_genuine_tie_is_consistent_not_bias():
    judge = first_position_judge({})
    pair = Pair("x", "q", "neutral", "also neutral")   # neither has BETTER
    r = judge_pair_debiased(pair, judge)
    assert r["winner"] == "tie"
    assert r["consistent"] and not r["position_bias"]


def test_aggregate_over_committed_dataset():
    pairs, prefers = [], {}
    for line in (HERE / "dataset.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        d = json.loads(line)
        pairs.append(Pair(d["id"], d["question"], d["answer_a"], d["answer_b"]))
        if d.get("mock_biased"):
            prefers[d["question"]] = "A"

    m = run_judgements(pairs, first_position_judge(prefers))
    assert m["n"] == 7
    assert m["a_win_rate"] == round(3 / 7, 4)   # q1, q3, q4
    assert m["b_win_rate"] == round(1 / 7, 4)   # q2
    assert m["tie_rate"] == round(3 / 7, 4)     # q5, q6 (biased) + q7 (genuine)
    assert m["position_bias_rate"] == round(2 / 7, 4)  # q5, q6

    committed = json.loads((HERE / "results" / "results.json").read_text(encoding="utf-8"))
    assert committed == m
