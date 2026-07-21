"""Tests for the prompt linter: each rule fires on a targeted prompt, a strong
prompt scores 100, a weak one scores low, and the committed report is pinned."""
import json
from pathlib import Path

from linter import lint

HERE = Path(__file__).resolve().parent.parent


def rules(prompt: str) -> set[str]:
    return {i["rule"] for i in lint(prompt)["issues"]}


def test_strong_prompt_is_clean():
    strong = (
        'Classify the ticket below into exactly one of: billing, shipping, technical. '
        'Respond with only the label.\n\nTicket:\n"""\nMy package never arrived.\n"""'
    )
    report = lint(strong)
    assert report["issues"] == []
    assert report["score"] == 100


def test_conflicting_length_detected():
    assert "conflicting_length" in rules("Summarize this comprehensively but keep it very short.")


def test_structured_without_example_detected():
    assert "no_example_for_structure" in rules("Extract entities and return JSON.")
    assert "no_example_for_structure" not in rules('Return JSON like {"a": 1}.')


def test_vague_and_shouting_detected():
    r = rules("WRITE A DETAILED GOOD ANSWER with several RELEVANT points AS NEEDED.")
    assert "vague_quantifier" in r
    assert "shouting" in r


def test_missing_format_and_task():
    r = rules("some information about this topic")
    assert "no_output_format" in r
    assert "unclear_task" in r


def test_score_drops_with_more_issues():
    good = lint('List exactly 3 pros. Respond as a numbered list.')["score"]
    bad = lint("Please kindly give me some detailed but brief notes about the text below.")["score"]
    assert good > bad


def test_committed_report_matches():
    prompts = [json.loads(x) for x in (HERE / "prompts.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    fresh = [{"id": p.get("id"), "note": p.get("note"), **lint(p["prompt"])} for p in prompts]
    committed = json.loads((HERE / "results" / "report.json").read_text(encoding="utf-8"))
    assert committed == fresh
