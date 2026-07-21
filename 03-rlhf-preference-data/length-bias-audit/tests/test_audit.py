"""Tests for the length-bias audit: a fully length-biased set is flagged strongly, a
balanced set is not, the point-biserial correlation behaves at the extremes, and the
committed dataset audit is pinned."""
import json
from pathlib import Path

from audit import audit, token_len

HERE = Path(__file__).resolve().parent.parent


def test_token_len():
    assert token_len("one two three") == 3
    assert token_len("") == 0


def test_all_longer_chosen_is_strong_bias():
    pairs = [
        {"chosen": "this is a much longer and more detailed answer here", "rejected": "short"},
        {"chosen": "again a considerably longer response with many more words", "rejected": "brief"},
        {"chosen": "yet another long winded chosen answer padded out", "rejected": "no"},
    ]
    r = audit(pairs)
    assert r["longer_chosen_rate"] == 1.0
    assert r["point_biserial"] > 0.35
    assert "strong length bias" in r["verdict"]


def test_balanced_set_has_low_bias():
    # chosen is longer half the time, shorter the other half -> no systematic signal
    pairs = [
        {"chosen": "a b c d e", "rejected": "one"},
        {"chosen": "two", "rejected": "a b c d e"},
        {"chosen": "a b c", "rejected": "x y z"},
        {"chosen": "p q", "rejected": "m n"},
    ]
    r = audit(pairs)
    assert r["longer_chosen_rate"] == 0.25
    assert abs(r["point_biserial"]) < 0.35
    assert "no strong length bias" in r["verdict"]


def test_empty():
    assert audit([])["verdict"] == "no data"


def test_pins_committed_results():
    pairs = [json.loads(x) for x in (HERE / "dataset.jsonl").read_text().splitlines() if x.strip()]
    r = audit(pairs)
    assert r["n"] == 8
    # six of eight pairs have the longer answer chosen -> visible but not extreme bias
    assert r["longer_chosen_rate"] == 0.75
    committed = json.loads((HERE / "results" / "results.json").read_text(encoding="utf-8"))
    assert committed == r
