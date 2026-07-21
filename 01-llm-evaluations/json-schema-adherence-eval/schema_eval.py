"""Evaluate how reliably model outputs conform to a required JSON schema.

Structured-output tasks ask the model to return JSON in a specific shape. "Did it
comply?" breaks into several failure modes: the output isn't valid JSON at all, it's
valid but the wrong type, a required field is missing, a field has the wrong type, or
an enum value is out of range. This module checks each output against a small schema
spec and reports a conformance rate plus a breakdown of *why* outputs failed — the
diagnostic you need to improve a structured-output prompt.

The schema spec is intentionally tiny (required keys, types, enums) so the checker is
transparent; it is not a full JSON Schema implementation.
"""
from __future__ import annotations

import json

_TYPES = {
    "string": str,
    "number": (int, float),
    "integer": int,
    "boolean": bool,
    "array": list,
    "object": dict,
}


def _type_ok(value: object, type_name: str) -> bool:
    expected = _TYPES[type_name]
    if type_name in ("number", "integer") and isinstance(value, bool):
        return False  # bool is a subclass of int but is not a number here
    return isinstance(value, expected)


def check(output: str, schema: dict) -> dict:
    """Check one raw output string against a schema spec.

    schema = {"fields": {name: {"type": ..., "required": bool, "enum": [...]?}}}
    Returns {"conformant": bool, "errors": [codes]}.
    """
    try:
        obj = json.loads(output)
    except (json.JSONDecodeError, ValueError):
        return {"conformant": False, "errors": ["invalid_json"]}

    if not isinstance(obj, dict):
        return {"conformant": False, "errors": ["not_an_object"]}

    errors: list[str] = []
    for name, spec in schema["fields"].items():
        if name not in obj:
            if spec.get("required", False):
                errors.append(f"missing:{name}")
            continue
        value = obj[name]
        if not _type_ok(value, spec["type"]):
            errors.append(f"type:{name}")
            continue
        if "enum" in spec and value not in spec["enum"]:
            errors.append(f"enum:{name}")
    return {"conformant": not errors, "errors": errors}


def evaluate(outputs: list[str], schema: dict) -> dict:
    per_item = [check(o, schema) for o in outputs]
    n = len(per_item)
    conformant = sum(1 for r in per_item if r["conformant"])

    # tally failure reasons by category (invalid_json, not_an_object, missing, type, enum)
    reasons: dict[str, int] = {}
    for r in per_item:
        for e in r["errors"]:
            key = e.split(":", 1)[0]
            reasons[key] = reasons.get(key, 0) + 1

    return {
        "n": n,
        "conformance_rate": round(conformant / n, 4) if n else 0.0,
        "n_conformant": conformant,
        "failure_reasons": dict(sorted(reasons.items())),
        "per_item": per_item,
    }
