"""Evaluate an agent's tool calls: are they valid, is the right tool chosen, and
are the arguments correct?

Given a catalog of tools (each with required/optional params and types) and a set of
tasks with an expected call, the harness scores an agent's produced call along three
axes — schema validity, tool selection, and argument correctness — and rolls them up
into rates you can track across agents or model versions.
"""
from __future__ import annotations

from collections.abc import Callable

# Tool catalog: name -> {required, optional, types}
TOOLS: dict[str, dict] = {
    "get_weather": {"required": ["city"], "optional": ["units"], "types": {"city": "str", "units": "str"}},
    "search_web": {"required": ["query"], "optional": ["max_results"], "types": {"query": "str", "max_results": "int"}},
    "send_email": {
        "required": ["to", "subject", "body"],
        "optional": [],
        "types": {"to": "str", "subject": "str", "body": "str"},
    },
    "create_event": {
        "required": ["title", "date"],
        "optional": ["location"],
        "types": {"title": "str", "date": "str", "location": "str"},
    },
    "convert_currency": {
        "required": ["amount", "from_currency", "to_currency"],
        "optional": [],
        "types": {"amount": "number", "from_currency": "str", "to_currency": "str"},
    },
}

_TYPES: dict[str, tuple[type, ...]] = {"str": (str,), "int": (int,), "number": (int, float)}

Agent = Callable[[str], dict]


def validate_call(call: dict) -> list[str]:
    """Return a list of schema errors for a {"tool", "args"} call; empty means valid."""
    errors: list[str] = []
    tool = call.get("tool")
    if tool not in TOOLS:
        return [f"unknown tool: {tool!r}"]
    spec = TOOLS[tool]
    args = call.get("args") or {}
    allowed = set(spec["required"]) | set(spec["optional"])

    for req in spec["required"]:
        if req not in args:
            errors.append(f"missing required arg: {req}")
    for key, value in args.items():
        if key not in allowed:
            errors.append(f"unexpected arg: {key}")
            continue
        expected = _TYPES[spec["types"][key]]
        if isinstance(value, bool) or not isinstance(value, expected):
            errors.append(f"wrong type for {key}: {type(value).__name__}")
    return errors


def score_task(task: dict, call: dict) -> dict:
    errors = validate_call(call)
    valid = not errors
    tool_correct = call.get("tool") == task["expected_tool"]
    args_correct = tool_correct and (call.get("args") or {}) == task["expected_args"]
    return {
        "id": task["id"],
        "valid": valid,
        "tool_correct": tool_correct,
        "args_correct": args_correct,
        "fully_correct": valid and tool_correct and args_correct,
        "errors": errors,
    }


def run_harness(tasks: list[dict], agent: Agent) -> dict:
    per_task = [score_task(t, agent(t["prompt"])) for t in tasks]
    n = len(per_task)
    tool_correct = sum(1 for r in per_task if r["tool_correct"])
    return {
        "n_tasks": n,
        "valid_rate": round(sum(r["valid"] for r in per_task) / n, 4) if n else 0.0,
        "tool_selection_accuracy": round(tool_correct / n, 4) if n else 0.0,
        "full_pass_rate": round(sum(r["fully_correct"] for r in per_task) / n, 4) if n else 0.0,
        "arg_match_given_correct_tool": round(
            sum(1 for r in per_task if r["args_correct"]) / tool_correct, 4
        )
        if tool_correct
        else None,
        "tasks": per_task,
    }


def mock_agent(prompt_to_call: dict[str, dict]) -> Agent:
    def agent(prompt: str) -> dict:
        return prompt_to_call.get(prompt, {"tool": None, "args": {}})

    return agent
