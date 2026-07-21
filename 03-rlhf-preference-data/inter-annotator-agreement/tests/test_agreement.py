"""Tests for the agreement metrics.

Cohen's and Fleiss' kappa are checked against hand-computable and textbook values
(the Fleiss example is the standard one whose kappa is ~0.210), so the implementation
is validated, not just exercised. A final test pins the committed sample report.
"""
import json
from pathlib import Path

from agreement import analyze, cohens_kappa, fleiss_kappa, percent_agreement

HERE = Path(__file__).resolve().parent.parent

# Standard Fleiss' kappa worked example: 10 subjects, 14 raters, 5 categories.
FLEISS_EXAMPLE = [
    [0, 0, 0, 0, 14],
    [0, 2, 6, 4, 2],
    [0, 0, 3, 5, 6],
    [0, 3, 9, 2, 0],
    [2, 2, 8, 1, 1],
    [7, 7, 0, 0, 0],
    [3, 2, 6, 3, 0],
    [2, 5, 3, 2, 2],
    [6, 5, 2, 1, 0],
    [0, 2, 2, 3, 7],
]


def test_percent_agreement():
    assert percent_agreement(["a", "b", "c"], ["a", "b", "c"]) == 1.0
    assert percent_agreement(["a", "b"], ["a", "c"]) == 0.5
    assert percent_agreement([], []) == 1.0


def test_cohens_kappa_known_value():
    # po = 0.75, pe = 0.5  ->  kappa = 0.5
    assert cohens_kappa([1, 1, 0, 0], [1, 0, 0, 0]) == 0.5


def test_cohens_kappa_perfect_and_chance():
    assert cohens_kappa(["a", "b", "c"], ["a", "b", "c"]) == 1.0
    # perfect disagreement with two categories -> negative kappa
    assert cohens_kappa(["a", "a", "b", "b"], ["b", "b", "a", "a"]) < 0


def test_fleiss_kappa_matches_textbook():
    k = fleiss_kappa(FLEISS_EXAMPLE)
    assert abs(k - 0.210) < 0.005


def test_fleiss_kappa_perfect():
    # every rater agrees on every item
    assert fleiss_kappa([[3, 0], [0, 3], [3, 0]]) == 1.0


def test_analyze_shapes_and_pins_committed_report():
    rows = [json.loads(x) for x in (HERE / "sample_data" / "annotations.jsonl").read_text().splitlines() if x.strip()]
    stats = analyze(rows)
    assert stats["n_items"] == 12
    assert stats["n_annotators"] == 3
    assert set(stats["categories"]) == {"A", "B", "tie"}
    assert stats["fleiss_kappa"] is not None  # 3 raters per item -> defined
    assert 0.0 < stats["mean_percent_agreement"] <= 1.0

    committed = json.loads((HERE / "results" / "report.json").read_text(encoding="utf-8"))
    assert committed == stats
