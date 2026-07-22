"""Tests for the refinement loop: the critic detects violations, the loop converges and
the final text satisfies the spec, keyword-vs-length does not oscillate (regression),
an impossible spec stops at the iteration cap, and the committed trajectory is pinned."""
import json
from pathlib import Path

from refine import critique, refine

HERE = Path(__file__).resolve().parent.parent


def test_critique_flags_violations():
    spec = {"max_words": 3, "must_end_with_period": True, "must_include": ["x"]}
    v = critique("this is way too long", spec)
    assert "too_long" in v and "no_end_period" in v and "missing:x" in v


def test_loop_converges_and_satisfies_spec():
    spec = {"max_words": 12, "must_end_with_period": True, "must_include": ["safety"], "no_trailing_space": True}
    result = refine("This  guide explains how the system works in considerable detail across many words", spec)
    assert result["converged"]
    assert critique(result["final_text"], spec) == []
    assert "safety" in result["final_text"].lower()


def test_keyword_and_length_do_not_oscillate():
    # regression: adding a required keyword must not be undone by the length trim
    spec = {"max_words": 4, "must_include": ["safety"]}
    result = refine("one two three four five six seven", spec)
    assert result["converged"]
    words = result["final_text"].split()
    assert len(words) <= 4
    assert "safety" in [w.lower() for w in words]


def test_impossible_spec_stops_at_cap():
    # max_words 0 with a required keyword can never be satisfied
    spec = {"max_words": 0, "must_include": ["needed"]}
    result = refine("some draft text", spec, max_iters=3)
    assert not result["converged"]
    assert result["iterations"] == 3


def test_pins_committed_trajectory():
    committed = json.loads((HERE / "results" / "results.json").read_text(encoding="utf-8"))
    spec = {"max_words": 12, "must_end_with_period": True, "must_include": ["safety"], "no_trailing_space": True}
    result = refine("This  guide explains how the system works in considerable detail across many words", spec)
    assert committed == result
    assert result["iterations"] == 2 and result["converged"]
