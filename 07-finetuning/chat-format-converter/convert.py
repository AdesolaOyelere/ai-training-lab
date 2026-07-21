"""Convert supervised fine-tuning data between the three common chat formats.

Every dataset seems to ship in a different shape; before you can train or mix
sources you have to normalize them. This converts between:

- "messages"        -> {"messages": [{"role": "user"|"assistant"|"system", "content": ...}]}
- "sharegpt"        -> {"conversations": [{"from": "human"|"gpt"|"system", "value": ...}]}
- "prompt_response" -> {"prompt": ..., "response": ..., "system"?: ...}  (single turn)

Everything is normalized to the "messages" form internally, then emitted in the
target format, so adding a new format only means writing two small functions.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FORMATS = ("messages", "sharegpt", "prompt_response")

_SHAREGPT_TO_ROLE = {"system": "system", "human": "user", "gpt": "assistant"}
_ROLE_TO_SHAREGPT = {"system": "system", "user": "human", "assistant": "gpt"}
_VALID_ROLES = set(_ROLE_TO_SHAREGPT)


def _validate_messages(messages: list[dict]) -> list[dict]:
    if not isinstance(messages, list) or not messages:
        raise ValueError("messages must be a non-empty list")
    for m in messages:
        if m.get("role") not in _VALID_ROLES:
            raise ValueError(f"invalid role: {m.get('role')!r}")
        if not isinstance(m.get("content"), str):
            raise ValueError("each message needs string content")
    return messages


def to_messages(record: dict, fmt: str) -> list[dict]:
    if fmt == "messages":
        return _validate_messages(record["messages"])
    if fmt == "sharegpt":
        msgs = []
        for turn in record["conversations"]:
            role = _SHAREGPT_TO_ROLE.get(turn.get("from"))
            if role is None:
                raise ValueError(f"unknown sharegpt sender: {turn.get('from')!r}")
            msgs.append({"role": role, "content": turn["value"]})
        return _validate_messages(msgs)
    if fmt == "prompt_response":
        msgs = []
        if record.get("system"):
            msgs.append({"role": "system", "content": record["system"]})
        msgs.append({"role": "user", "content": record["prompt"]})
        msgs.append({"role": "assistant", "content": record["response"]})
        return _validate_messages(msgs)
    raise ValueError(f"unknown format: {fmt}")


def from_messages(messages: list[dict], fmt: str) -> dict:
    _validate_messages(messages)
    if fmt == "messages":
        return {"messages": messages}
    if fmt == "sharegpt":
        return {"conversations": [{"from": _ROLE_TO_SHAREGPT[m["role"]], "value": m["content"]} for m in messages]}
    if fmt == "prompt_response":
        system = [m for m in messages if m["role"] == "system"]
        users = [m for m in messages if m["role"] == "user"]
        assistants = [m for m in messages if m["role"] == "assistant"]
        if len(users) != 1 or len(assistants) != 1 or len(system) > 1:
            raise ValueError("prompt_response only supports a single user/assistant turn")
        out = {"prompt": users[0]["content"], "response": assistants[0]["content"]}
        if system:
            out["system"] = system[0]["content"]
        return out
    raise ValueError(f"unknown format: {fmt}")


def convert_record(record: dict, src: str, dst: str) -> dict:
    return from_messages(to_messages(record, src), dst)


def convert_file(lines: list[str], src: str, dst: str) -> list[dict]:
    out = []
    for i, line in enumerate(lines, start=1):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(convert_record(json.loads(line), src, dst))
        except (KeyError, ValueError) as exc:
            raise ValueError(f"line {i}: {exc}") from exc
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="input .jsonl")
    ap.add_argument("--from", dest="src", required=True, choices=FORMATS)
    ap.add_argument("--to", dest="dst", required=True, choices=FORMATS)
    ap.add_argument("-o", "--out", help="output .jsonl (default: stdout)")
    args = ap.parse_args(argv)

    lines = Path(args.path).read_text(encoding="utf-8").splitlines()
    try:
        records = convert_file(lines, args.src, args.dst)
    except ValueError as exc:
        print(f"conversion error: {exc}", file=sys.stderr)
        return 1

    text = "".join(json.dumps(r) + "\n" for r in records)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {len(records)} records to {args.out}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
