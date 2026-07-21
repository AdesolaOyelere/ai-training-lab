"""Tests for the chat-format converter: role mapping, round trips, single-turn
constraints, validation, and the CLI over the committed sample."""
import json
from pathlib import Path

import pytest
from convert import convert_file, convert_record, from_messages, main, to_messages

HERE = Path(__file__).resolve().parent.parent

SHAREGPT = {
    "conversations": [
        {"from": "system", "value": "sys"},
        {"from": "human", "value": "hi"},
        {"from": "gpt", "value": "hello"},
    ]
}


def test_sharegpt_to_messages_role_mapping():
    msgs = to_messages(SHAREGPT, "sharegpt")
    assert msgs == [
        {"role": "system", "content": "sys"},
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
    ]


def test_sharegpt_messages_round_trip():
    msgs = to_messages(SHAREGPT, "sharegpt")
    back = from_messages(msgs, "sharegpt")
    assert back == SHAREGPT


def test_prompt_response_round_trip_single_turn():
    pr = {"system": "sys", "prompt": "q", "response": "a"}
    msgs = to_messages(pr, "prompt_response")
    assert from_messages(msgs, "prompt_response") == pr


def test_multiturn_cannot_become_prompt_response():
    multiturn = {
        "messages": [
            {"role": "user", "content": "a"},
            {"role": "assistant", "content": "b"},
            {"role": "user", "content": "c"},
            {"role": "assistant", "content": "d"},
        ]
    }
    with pytest.raises(ValueError):
        convert_record(multiturn, "messages", "prompt_response")


def test_validation_rejects_bad_role():
    with pytest.raises(ValueError):
        to_messages({"messages": [{"role": "bot", "content": "x"}]}, "messages")


def test_convert_file_reports_line_number():
    lines = ['{"messages": [{"role": "user", "content": "ok"}, {"role": "assistant", "content": "y"}]}',
             '{"messages": [{"role": "user", "content": "a"}, {"role": "assistant", "content": "b"},'
             ' {"role": "user", "content": "c"}, {"role": "assistant", "content": "d"}]}']
    with pytest.raises(ValueError, match="line 2"):
        convert_file(lines, "messages", "prompt_response")


def test_cli_sharegpt_to_messages(tmp_path, capsys):
    out = tmp_path / "messages.jsonl"
    rc = main([str(HERE / "sample_data" / "sharegpt.jsonl"), "--from", "sharegpt", "--to", "messages", "-o", str(out)])
    assert rc == 0
    records = [json.loads(x) for x in out.read_text(encoding="utf-8").splitlines() if x.strip()]
    assert len(records) == 2
    assert records[0]["messages"][0] == {"role": "system", "content": "You are a helpful assistant."}
    assert records[1]["messages"][-1] == {"role": "assistant", "content": "Red."}
