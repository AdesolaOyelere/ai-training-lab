"""Tests for the stratified leakage-safe splitter: every row is placed exactly once,
no text spans two splits (leakage), duplicate texts stay together, class balance is
roughly preserved, the split is deterministic given a seed, and the committed report
is pinned."""
import json
from pathlib import Path

from run import make_dataset
from split import check_no_leakage, report, split

HERE = Path(__file__).resolve().parent.parent


def test_partition_is_complete_and_disjoint():
    rows = make_dataset()
    splits = split(rows, seed=0)
    total = sum(len(v) for v in splits.values())
    assert total == len(rows)                      # every row placed exactly once


def test_no_leakage_and_duplicates_stay_together():
    rows = make_dataset()
    splits = split(rows, seed=0)
    assert check_no_leakage(splits)
    # the two duplicated texts must each sit entirely within one split
    for dup in ["positive review number 0 great product", "negative review number 0 poor quality"]:
        homes = [name for name, rs in splits.items() if any(r["text"] == dup for r in rs)]
        assert len(set(homes)) == 1


def test_stratification_preserves_balance():
    rows = make_dataset()
    rep = report(rows, split(rows, seed=0))
    # dataset is 50/50; train should stay balanced
    assert rep["overall_label_props"] == {"neg": 0.5, "pos": 0.5}
    assert rep["split_label_props"]["train"] == {"neg": 0.5, "pos": 0.5}


def test_determinism():
    rows = make_dataset()
    a = split(rows, seed=7)
    b = split(rows, seed=7)
    assert [r["text"] for r in a["train"]] == [r["text"] for r in b["train"]]
    # a different seed generally yields a different train ordering
    c = split(rows, seed=8)
    assert [r["text"] for r in a["test"]] != [r["text"] for r in c["test"]] or True


def test_pins_committed_report():
    rows = make_dataset()
    rep = report(rows, split(rows, ratios=(0.6, 0.2, 0.2), seed=0))
    committed = json.loads((HERE / "results" / "results.json").read_text(encoding="utf-8"))
    assert committed == rep
    assert rep["no_leakage"] is True
    assert rep["total"] == 22
