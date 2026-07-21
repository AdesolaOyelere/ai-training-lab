"""Tests for the answer grader: numeric normalization, fraction equivalence, text
labels, the "picks the final answer not an intermediate number" behavior, and the
pinned dataset grading (which includes one deliberately wrong model answer)."""
import json
from pathlib import Path

from grader import check_fraction, check_numeric, check_text, grade_dataset, parse_number

HERE = Path(__file__).resolve().parent.parent


def test_number_normalization():
    assert parse_number("the total is $1,200.00") == 1200.0
    assert check_numeric("Final answer: 1,200", 1200)
    assert check_numeric("I get 1200.0 exactly", 1200)
    assert not check_numeric("the answer is 1201", 1200)


def test_uses_final_answer_not_intermediate():
    # intermediate 10 appears, but the marked final answer is 30
    assert check_numeric("40 - 10 discount ... Final answer: 30", 30)
    # a wrong final answer must fail even if the right number appears earlier
    assert not check_numeric("40 - 10 = 30 ... but the answer is 25", 30)


def test_fraction_equivalence():
    assert check_fraction("that reduces to 1/4", "1/4")
    assert check_fraction("so 3/12", "1/4")          # unreduced but equal
    assert not check_fraction("the answer is 1/3", "1/4")


def test_text_label_normalization():
    assert check_text("Answer: No.", "no")
    assert check_text("so it is not prime. Answer: No", "no")
    assert not check_text("Answer: Yes", "no")


def test_grade_dataset_pins_committed_results():
    items = [json.loads(x) for x in (HERE / "dataset.jsonl").read_text().splitlines() if x.strip()]
    outs = {r["id"]: r["output"] for r in
            (json.loads(x) for x in (HERE / "model_outputs.jsonl").read_text().splitlines() if x.strip())}
    m = grade_dataset(items, outs)
    assert m["n"] == 8
    # m7 has a wrong final answer (25 instead of 30) -> 7/8 correct
    assert m["accuracy"] == 0.875
    wrong = [r["id"] for r in m["per_item"] if not r["correct"]]
    assert wrong == ["m7"]

    committed = json.loads((HERE / "results" / "results.json").read_text(encoding="utf-8"))
    assert committed == m
