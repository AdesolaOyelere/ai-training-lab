"""Tests for the tool-calling harness: schema validation catches unknown tools,
missing args, unexpected args, and wrong types; scoring distinguishes tool errors
from argument errors; and the aggregate over the committed tasks is pinned."""
import json
from pathlib import Path

from harness import mock_agent, run_harness, score_task, validate_call

HERE = Path(__file__).resolve().parent.parent


def test_validate_accepts_good_call():
    assert validate_call({"tool": "get_weather", "args": {"city": "Paris"}}) == []
    assert validate_call({"tool": "get_weather", "args": {"city": "Paris", "units": "celsius"}}) == []


def test_validate_catches_schema_errors():
    assert validate_call({"tool": "nope", "args": {}})[0].startswith("unknown tool")
    assert "missing required arg: to" in validate_call({"tool": "send_email", "args": {"subject": "s", "body": "b"}})
    assert any("unexpected arg" in e for e in validate_call({"tool": "get_weather", "args": {"city": "x", "zip": "1"}}))
    type_errs = validate_call({"tool": "search_web", "args": {"query": "x", "max_results": "5"}})
    assert any("wrong type" in e for e in type_errs)


def test_bool_is_not_an_int():
    errs = validate_call({"tool": "search_web", "args": {"query": "x", "max_results": True}})
    assert any("wrong type" in e for e in errs)


def test_score_task_separates_tool_and_arg_errors():
    task = {"id": "x", "prompt": "p", "expected_tool": "get_weather", "expected_args": {"city": "Paris"}}
    wrong_tool = score_task(task, {"tool": "search_web", "args": {"query": "Paris"}})
    assert not wrong_tool["tool_correct"] and not wrong_tool["fully_correct"]
    wrong_args = score_task(task, {"tool": "get_weather", "args": {"city": "London"}})
    assert wrong_args["tool_correct"] and not wrong_args["args_correct"]


def test_aggregate_over_committed_tasks():
    tasks = [json.loads(x) for x in (HERE / "tasks.jsonl").read_text().splitlines() if x.strip()]
    agent = mock_agent({t["prompt"]: {"tool": t["mock_tool"], "args": t["mock_args"]} for t in tasks})
    m = run_harness(tasks, agent)
    assert m["n_tasks"] == 8
    assert m["valid_rate"] == 0.75            # t5 missing arg, t8 wrong type
    assert m["tool_selection_accuracy"] == 0.875  # t4 picks the wrong tool
    assert m["full_pass_rate"] == 0.5
    committed = json.loads((HERE / "results" / "results.json").read_text(encoding="utf-8"))
    assert committed == m
