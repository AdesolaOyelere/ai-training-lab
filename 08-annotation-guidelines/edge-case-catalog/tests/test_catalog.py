"""Tests for the edge-case detector: each case is detected, multiple cases can co-occur,
clean text is not flagged, and the detector reproduces every gold routing (so the
catalog doc and the code stay in sync)."""
import json
from pathlib import Path

from catalog import detect_edge_cases, needs_careful_review, route

HERE = Path(__file__).resolve().parent.parent


def test_each_case():
    assert detect_edge_cases("I do not like it") == ["negation"]
    assert detect_edge_cases("good but slow") == ["contrast_mixed"]
    assert detect_edge_cases("oh great, broken again") == ["sarcasm_cue"]
    assert detect_edge_cases("better than before") == ["comparison"]
    assert detect_edge_cases("why bother?") == ["rhetorical_question"]
    assert detect_edge_cases("I would have liked it if it were free") == ["conditional"]


def test_multiple_cases_cooccur():
    cases = detect_edge_cases("It is not bad, but slow.")
    assert cases == ["contrast_mixed", "negation"]


def test_clean_text_not_flagged():
    assert detect_edge_cases("It works fine and I am happy.") == []
    assert not needs_careful_review("A perfectly clear positive statement.")


def test_detector_reproduces_gold_routing():
    gold = json.loads((HERE / "gold_examples.json").read_text(encoding="utf-8"))
    for g in gold:
        assert detect_edge_cases(g["text"]) == sorted(g["expected"]), g["id"]


def test_route_report_pins_committed():
    gold = json.loads((HERE / "gold_examples.json").read_text(encoding="utf-8"))
    report = route([{"id": g["id"], "text": g["text"]} for g in gold])
    report["gold_mismatches"] = [g["id"] for g in gold if detect_edge_cases(g["text"]) != sorted(g["expected"])]
    assert report["gold_mismatches"] == []
    committed = json.loads((HERE / "results" / "results.json").read_text(encoding="utf-8"))
    assert committed == report
