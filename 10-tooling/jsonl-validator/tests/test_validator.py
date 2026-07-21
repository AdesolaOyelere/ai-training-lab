"""Tests for the JSONL validator: field rules, type checks, uniqueness, and the
end-to-end behavior over the committed good/bad sample files."""
from pathlib import Path

from jsonl_validator import main, validate_lines

HERE = Path(__file__).resolve().parent.parent


def kinds(issues):
    return sorted(i.kind for i in issues)


def test_clean_file_has_no_issues():
    lines = (HERE / "sample_data" / "good.jsonl").read_text(encoding="utf-8").splitlines()
    issues = validate_lines(lines, require=["id", "prompt", "response"], types={"score": "number"}, unique="id")
    assert issues == []


def test_bad_file_reports_every_problem():
    lines = (HERE / "sample_data" / "bad.jsonl").read_text(encoding="utf-8").splitlines()
    issues = validate_lines(lines, require=["id", "prompt", "response"], types={"score": "number"}, unique="id")
    assert kinds(issues) == sorted(
        ["empty_field", "duplicate_key", "wrong_type", "missing_field", "invalid_json", "not_an_object"]
    )
    # duplicate points back to the first occurrence
    dup = next(i for i in issues if i.kind == "duplicate_key")
    assert "line 2" in dup.detail


def test_missing_and_empty_fields():
    lines = ['{"id": "a", "text": ""}', '{"id": "b"}']
    issues = validate_lines(lines, require=["id", "text"])
    assert kinds(issues) == ["empty_field", "missing_field"]


def test_type_checks_and_bool_is_not_a_number():
    lines = ['{"n": 3}', '{"n": true}', '{"n": "x"}']
    issues = validate_lines(lines, types={"n": "number"})
    # the integer passes; the bool and the string both fail
    assert len(issues) == 2
    assert all(i.kind == "wrong_type" for i in issues)


def test_unknown_type_is_flagged():
    issues = validate_lines(['{"x": 1}'], types={"x": "widget"})
    assert kinds(issues) == ["unknown_type"]


def test_blank_lines_configurable():
    lines = ['{"id": 1}', "", "   ", '{"id": 2}']
    assert validate_lines(lines) == []
    assert len(validate_lines(lines, allow_blank=False)) == 2


def test_cli_exit_codes(capsys):
    good = str(HERE / "sample_data" / "good.jsonl")
    bad = str(HERE / "sample_data" / "bad.jsonl")
    assert main([good, "--require", "id,prompt,response", "--unique", "id"]) == 0
    assert main([bad, "--require", "id,prompt,response", "--types", "score:number", "--unique", "id"]) == 1
    assert main(["does-not-exist.jsonl"]) == 2
