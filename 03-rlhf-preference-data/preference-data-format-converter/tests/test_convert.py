"""Tests for the preference-format converter: pairwise<->ranked round trips, ranked
expands to all ordered pairs, binary labels split the ranking, single-response binary
round-trips its label, and errors report the record index."""
import json
from pathlib import Path

import pytest
from convert import convert, convert_record

HERE = Path(__file__).resolve().parent.parent


def test_pairwise_ranked_round_trip():
    pw = {"prompt": "p", "chosen": "A", "rejected": "B"}
    ranked = convert_record(pw, "pairwise", "ranked")[0]
    assert ranked["responses"] == ["A", "B"]
    back = convert_record(ranked, "ranked", "pairwise")[0]
    assert back == pw


def test_ranked_expands_to_all_ordered_pairs():
    ranked = {"prompt": "p", "responses": ["best", "mid", "worst"]}
    pairs = convert_record(ranked, "ranked", "pairwise")
    assert len(pairs) == 3
    assert {"prompt": "p", "chosen": "best", "rejected": "worst"} in pairs
    assert {"prompt": "p", "chosen": "mid", "rejected": "worst"} in pairs
    # a better response is never rejected in favor of a worse one
    for pr in pairs:
        assert ranked["responses"].index(pr["chosen"]) < ranked["responses"].index(pr["rejected"])


def test_binary_labels_split_the_ranking():
    ranked = {"prompt": "p", "responses": ["a", "b", "c", "d"]}
    rows = convert_record(ranked, "ranked", "binary")
    labels = [r["label"] for r in rows]
    assert labels == [True, True, False, False]     # top half desirable


def test_binary_single_row_round_trips_label():
    row = {"prompt": "p", "completion": "x", "label": False}
    ranked = convert_record(row, "binary", "ranked")[0]
    assert ranked["responses"] == ["x"]
    back = convert_record(ranked, "ranked", "binary")[0]
    assert back == row


def test_error_reports_index():
    recs = [{"prompt": "p", "responses": ["only one"]}]  # can't make a pair from 1
    with pytest.raises(ValueError, match="record 0"):
        convert(recs, "ranked", "pairwise")


def test_pins_committed_results():
    ranked = [json.loads(x) for x in (HERE / "sample_data" / "ranked.jsonl").read_text().splitlines() if x.strip()]
    pairwise = convert(ranked, "ranked", "pairwise")
    binary = convert(ranked, "ranked", "binary")
    assert len(pairwise) == 4 and len(binary) == 5
    committed = json.loads((HERE / "results" / "results.json").read_text(encoding="utf-8"))
    assert committed["n_pairwise"] == 4 and committed["n_binary"] == 5
