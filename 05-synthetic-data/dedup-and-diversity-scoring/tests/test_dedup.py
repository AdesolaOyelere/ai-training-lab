"""Tests for dedup and diversity: similarity behaves sensibly, near-duplicates are
removed while distinct items are kept, diversity rises after dedup, and the analysis
over the committed dataset is pinned."""
import json
from pathlib import Path

from dedup import analyze, dedupe, diversity_score, similarity

HERE = Path(__file__).resolve().parent.parent


def test_similarity_bounds():
    assert similarity("hello world", "hello world") == 1.0
    assert similarity("abcdefgh", "zzzzzzzz") == 0.0
    near = similarity("the sum of two numbers", "the sum of two integers")
    assert 0.4 < near < 1.0


def test_dedupe_removes_near_duplicates():
    texts = [
        "Write a function that returns the sum of two numbers.",
        "Write a function that returns the sum of two integers.",
        "Explain how a hash table works.",
    ]
    r = dedupe(texts, threshold=0.7)
    assert r["n_kept"] == 2                      # first two are near-dups
    assert r["removed"][0]["duplicate_of"] == 0


def test_distinct_items_are_kept():
    texts = ["apples and oranges", "quantum entanglement basics", "the history of jazz"]
    r = dedupe(texts, threshold=0.8)
    assert r["n_kept"] == 3
    assert r["n_removed"] == 0


def test_diversity_increases_after_dedup():
    texts = ["same thing here", "same thing here", "a totally different sentence"]
    m = analyze(texts, threshold=0.9)
    assert m["diversity_after"] >= m["diversity_before"]
    assert diversity_score(["only one"]) == 1.0


def test_analysis_pins_committed_results():
    rows = [json.loads(x) for x in (HERE / "dataset.jsonl").read_text().splitlines() if x.strip()]
    m = analyze([r["text"] for r in rows], threshold=0.6)
    # d2 and d5 are near-dups of d1; d7 is a near-dup of d3
    assert m["n_kept"] == 5
    assert m["n_removed"] == 3
    committed = json.loads((HERE / "results" / "results.json").read_text(encoding="utf-8"))
    assert committed == m
