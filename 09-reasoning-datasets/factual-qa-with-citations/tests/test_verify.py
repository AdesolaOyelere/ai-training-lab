"""Tests for citation verification: a well-cited answer is grounded, a wrong citation is
caught (low support), an uncited claim fails, an invalid citation id is flagged, and the
committed aggregate over the mixed dataset is pinned."""
import json
from pathlib import Path

from verify import evaluate, verify_item

HERE = Path(__file__).resolve().parent.parent


def item(answer, citations):
    return {
        "id": "t",
        "question": "q",
        "source": [{"id": "s1", "text": "the battery lasts twelve hours"},
                   {"id": "s2", "text": "it ships in three colors"}],
        "answer": answer,
        "citations": citations,
    }


def test_well_cited_answer_is_grounded():
    r = verify_item(item("the battery lasts twelve hours", ["s1"]))
    assert r["grounded"] and r["support"] == 1.0 and r["invalid_citations"] == []


def test_wrong_citation_is_caught():
    # correct answer but cites the unrelated sentence -> not grounded
    r = verify_item(item("the battery lasts twelve hours", ["s2"]))
    assert not r["grounded"] and r["support"] < 0.6


def test_uncited_claim_fails():
    # cites s1 but the answer adds content not supported there
    r = verify_item(item("the battery has ancient temples and gold", ["s1"]))
    assert not r["grounded"]


def test_invalid_citation_flagged():
    r = verify_item(item("the battery lasts twelve hours", ["s9"]))
    assert r["invalid_citations"] == ["s9"]
    assert not r["has_valid_citation"] and not r["grounded"]


def test_pins_committed_results():
    items = [json.loads(x) for x in (HERE / "dataset.jsonl").read_text().splitlines() if x.strip()]
    m = evaluate(items)
    assert m["n"] == 5
    assert m["grounded_rate"] == 0.4          # c1, c2 grounded; c3/c4/c5 fail differently
    assert m["n_with_invalid_citations"] == 1
    committed = json.loads((HERE / "results" / "results.json").read_text(encoding="utf-8"))
    assert committed == m
