"""Tests for the SFT prep pipeline: each drop reason fires, whitespace is normalized,
duplicates are caught case-insensitively, system prompts survive, output is valid
messages format, and the report over the committed raw file is pinned."""
import json
from pathlib import Path

from prepare import is_placeholder, normalize_ws, prepare

HERE = Path(__file__).resolve().parent.parent


def test_normalize_and_placeholder():
    assert normalize_ws("  a\n b\t c ") == "a b c"
    assert is_placeholder("TODO") and is_placeholder("n/a")
    assert not is_placeholder("a real answer")


def test_each_drop_reason():
    rows = [
        {"response": "no prompt"},                                  # missing field
        {"prompt": "", "response": "x"},                            # empty
        {"prompt": "TBD", "response": "TBD"},                       # placeholder
        {"prompt": "ab", "response": "y"},                          # too short (prompt < 3)
        {"prompt": "hello", "response": "world"},                   # ok
        {"prompt": "hello", "response": "world"},                   # duplicate
        {"prompt": "ok prompt", "response": "z" * 5000},            # too long
    ]
    rep = prepare(rows)["report"]
    assert rep["dropped_missing_field"] == 1
    assert rep["dropped_empty"] == 1
    assert rep["dropped_placeholder"] == 1
    assert rep["dropped_too_short"] == 1
    assert rep["dropped_duplicate"] == 1
    assert rep["dropped_too_long"] == 1
    assert rep["kept"] == 1


def test_duplicate_is_case_insensitive_after_normalize():
    rows = [
        {"prompt": "Same Q", "response": "Same A"},
        {"prompt": "same q", "response": "same a  "},   # dup after normalize+lower
    ]
    assert prepare(rows)["report"]["kept"] == 1


def test_system_prompt_preserved_and_valid_messages():
    rows = [{"prompt": "question", "response": "answer", "system": "be terse"}]
    rec = prepare(rows)["records"][0]
    assert rec["messages"][0] == {"role": "system", "content": "be terse"}
    roles = [m["role"] for m in rec["messages"]]
    assert roles == ["system", "user", "assistant"]


def test_pins_committed_report():
    rows = [json.loads(x) for x in (HERE / "raw.jsonl").read_text().splitlines() if x.strip()]
    result = prepare(rows)
    rep = result["report"]
    assert rep["input"] == 12
    assert rep["kept"] == 5
    assert rep["dropped_empty"] == 3      # empty prompt, whitespace response, empty response
    assert rep["dropped_placeholder"] == 2  # TODO/TODO and the N/A response
    committed = json.loads((HERE / "results" / "report.json").read_text(encoding="utf-8"))
    assert committed == rep
