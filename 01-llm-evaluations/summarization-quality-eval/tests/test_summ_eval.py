"""Tests for the summary-quality metrics: coverage rewards captured key points,
faithfulness penalizes invented content, conciseness rewards compression, and the
aggregate over the committed dataset (with one incomplete and one hallucinated summary)
is pinned."""
import json
from pathlib import Path

from summ_eval import conciseness, coverage, evaluate, faithfulness

HERE = Path(__file__).resolve().parent.parent


def test_coverage():
    kps = ["battery lasts long", "waterproof design"]
    assert coverage("the battery lasts long and it is waterproof", kps) == 1.0
    assert coverage("only the battery lasts long", kps) == 0.5
    assert coverage("nothing relevant here", kps) == 0.0


def test_faithfulness_penalizes_invented_content():
    source = "the car is red and fast"
    assert faithfulness("the car is fast", source) == 1.0
    # "purple" and "spaceship" are not in the source -> lower faithfulness
    assert faithfulness("the purple spaceship is fast", source) < 1.0


def test_conciseness():
    assert conciseness("short", "this is a much longer source text with many words") > 0.5
    # summary longer than source -> 0
    assert conciseness("a b c d e f", "a b c") == 0.0


def test_aggregate_pins_committed():
    items = [json.loads(x) for x in (HERE / "dataset.jsonl").read_text().splitlines() if x.strip()]
    m = evaluate(items)
    assert m["n"] == 4
    per = {r["id"]: r for r in m["per_item"]}
    # d2 is incomplete (low coverage) but faithful
    assert per["d2"]["coverage"] == 0.4 and per["d2"]["faithfulness"] == 1.0
    # d3 hallucinates (chocolate/raspberries) and is bloated
    assert per["d3"]["faithfulness"] < 0.7 and per["d3"]["conciseness"] == 0.0
    committed = json.loads((HERE / "results" / "results.json").read_text(encoding="utf-8"))
    assert committed == m
