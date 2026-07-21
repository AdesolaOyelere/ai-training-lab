"""Unit tests for the instruction-following eval.

The checkers are the load-bearing part of the eval, so they get direct
true/false coverage. The final test runs the whole eval over the committed
dataset via the mock provider and pins the aggregate scores, which doubles as a
regression test for the sample results.
"""
import json
from pathlib import Path

from eval import Constraint, EvalItem, load_dataset, run_eval, score_output
from providers import mock_provider

HERE = Path(__file__).resolve().parent.parent


def c(type_, **params):
    return Constraint(type_, params)


def test_word_count_bounds():
    assert c("word_count_max", n=3).check("one two three")
    assert not c("word_count_max", n=2).check("one two three")
    assert c("word_count_min", n=3).check("one two three")
    assert not c("word_count_min", n=4).check("one two three")


def test_include_exclude_case_insensitive():
    assert c("must_include_all", substrings=["Ada", "AGE"]).check("name ada, age 30")
    assert not c("must_include_all", substrings=["missing"]).check("hello")
    assert c("must_not_include", substrings=["!", "?"]).check("no punctuation here")
    assert not c("must_not_include", substrings=["x"]).check("axb")


def test_start_end():
    assert c("starts_with", prefix="Remember:").check("  Remember: do it.")
    assert not c("starts_with", prefix="Remember:").check("Note: do it.")
    assert c("ends_with", suffix=".").check("done.  ")
    assert not c("ends_with", suffix=".").check("done")


def test_json_checks():
    assert c("json_valid").check('{"a": 1}')
    assert not c("json_valid").check("{not json}")
    assert c("json_has_keys", keys=["name", "age"]).check('{"name": "Ada", "age": 30}')
    assert not c("json_has_keys", keys=["name", "age"]).check('{"name": "Ada"}')


def test_structure_checks():
    assert c("exact_line_count", n=2).check("a\n\nb\n")
    assert not c("exact_line_count", n=2).check("a\nb\nc")
    assert c("max_sentences", n=2).check("One. Two.")
    assert not c("max_sentences", n=1).check("One. Two.")
    assert c("no_markdown").check("plain text only")
    assert not c("no_markdown").check("some **bold** text")
    assert c("regex_match", pattern=r"(?m)^- .+").check("- item\n- item")


def test_forbidden_words_is_word_boundary_aware():
    # "class" must not trigger on "classic"
    assert c("forbidden_words", words=["class"]).check("a classic example")
    assert not c("forbidden_words", words=["class"]).check("the class started")


def test_score_output_counts():
    item = EvalItem(
        id="t",
        prompt="p",
        constraints=[c("word_count_max", n=2), c("must_include_all", substrings=["x"])],
    )
    r = score_output(item, "x y")  # 2 words ok, includes x
    assert r["all_passed"] and r["n_passed"] == 2
    r2 = score_output(item, "a b c")  # too many words, missing x
    assert not r2["all_passed"] and r2["n_passed"] == 0


def test_full_eval_over_committed_dataset():
    items = load_dataset(str(HERE / "dataset.jsonl"))
    gen = mock_provider({it.prompt: it.mock_response for it in items})
    results = run_eval(items, gen)

    assert results["n_items"] == 8
    # Two items have one intentionally violated constraint each (over-long list,
    # missing final period); the rest are perfect.
    assert results["mean_constraint_satisfaction"] == 0.875
    assert results["perfect_rate"] == 0.75

    # The committed results file must match a fresh run.
    committed = json.loads((HERE / "results" / "results.json").read_text(encoding="utf-8"))
    assert committed["mean_constraint_satisfaction"] == results["mean_constraint_satisfaction"]
    assert committed["perfect_rate"] == results["perfect_rate"]
