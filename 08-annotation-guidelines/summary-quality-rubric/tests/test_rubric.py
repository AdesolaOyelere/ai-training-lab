"""Tests for the rubric: validation, weighted score, the faithfulness gate, the
coverage requirement for accept, and — most importantly — that the documented rules
reproduce every gold calibration label (guideline and code cannot drift apart)."""
import json
from pathlib import Path

import pytest
from rubric import decision, score_against_gold, validate, weighted_score

HERE = Path(__file__).resolve().parent.parent


def r(cov, faith, con, flu):
    return {"coverage": cov, "faithfulness": faith, "conciseness": con, "fluency": flu}


def test_validate_rejects_bad_input():
    with pytest.raises(ValueError):
        validate(r(4, 4, 4, 5))          # out of range
    with pytest.raises(ValueError):
        validate({"coverage": 4})        # missing dimensions
    with pytest.raises(ValueError):
        validate(r(True, 4, 4, 4))       # bool is not a valid score


def test_weighted_score():
    assert weighted_score(r(4, 4, 4, 4)) == 4.0
    assert weighted_score(r(1, 1, 1, 1)) == 1.0
    assert weighted_score(r(4, 4, 3, 3)) == 3.7


def test_faithfulness_gate_overrides_everything():
    # perfect on every other axis, but faithfulness 1 -> reject
    assert decision(r(4, 1, 4, 4)) == "reject"


def test_coverage_required_for_accept():
    # faithful, fluent, concise, but thin coverage -> revise, not accept
    assert decision(r(2, 4, 4, 4)) == "revise"
    assert decision(r(3, 3, 3, 3)) == "accept"


def test_low_scores_reject():
    assert decision(r(1, 2, 2, 2)) == "reject"


def test_rules_reproduce_gold_labels():
    gold = json.loads((HERE / "gold_examples.json").read_text(encoding="utf-8"))
    report = score_against_gold(gold)
    assert report["mismatches"] == []
    assert report["agreement"] == 1.0
    assert report["n"] == 7
