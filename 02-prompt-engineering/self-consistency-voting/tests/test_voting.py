"""Tests for self-consistency voting: answer normalization, majority selection with a
deterministic tie-break, the honest case where voting still fails (model wrong most of
the time), and the pinned aggregate showing voting beats single-sample accuracy."""
import json
from pathlib import Path

from voting import evaluate, majority_vote, normalize

HERE = Path(__file__).resolve().parent.parent


def test_normalization_groups_equivalent_answers():
    assert normalize("$1,200.") == "1200"
    assert normalize("  Paris ") == "paris"


def test_majority_vote_and_agreement():
    winner, agr = majority_vote(["12", "12", "10", "12", "9"])
    assert winner == "12"
    assert agr == 0.6


def test_tie_break_is_deterministic():
    # two answers tie at 1 each; the earliest in order wins
    winner, agr = majority_vote(["a", "b"])
    assert winner == "a" and agr == 0.5


def test_voting_can_still_fail_when_model_is_mostly_wrong():
    # gold is 3 but the model says 4 three times -> vote is wrong (honest limitation)
    m = evaluate([{"id": "x", "gold": "3", "samples": ["4", "4", "3", "4", "5"]}])
    assert m["majority_vote_accuracy"] == 0.0


def test_pins_committed_and_voting_beats_single():
    items = [json.loads(x) for x in (HERE / "dataset.jsonl").read_text().splitlines() if x.strip()]
    m = evaluate(items)
    assert m["n"] == 8
    assert m["majority_vote_accuracy"] == 0.875
    assert m["single_sample_accuracy_first"] == 0.375
    # the headline result: self-consistency beats a single sample
    assert m["majority_vote_accuracy"] > m["single_sample_accuracy_expected"]
    committed = json.loads((HERE / "results" / "results.json").read_text(encoding="utf-8"))
    assert committed == m
