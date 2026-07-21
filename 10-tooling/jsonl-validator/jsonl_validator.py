#!/usr/bin/env python3
"""Validate JSONL dataset files — the kind used for SFT, evals, and preference data.

Checks, per line: valid JSON, that each record is an object, required fields are
present and non-empty, optional type constraints hold, and (optionally) that a key
field is unique across the file. Reports every problem with its line number and
exits non-zero if any are found, so it drops straight into CI or a pre-commit hook.

Usage:
    python jsonl_validator.py data.jsonl --require id,prompt,response --unique id
    python jsonl_validator.py data.jsonl --require id --types id:str,score:number
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass

_TYPE_ALIASES = {
    "str": (str,),
    "string": (str,),
    "int": (int,),
    "number": (int, float),
    "float": (float, int),
    "bool": (bool,),
    "list": (list,),
    "array": (list,),
    "object": (dict,),
    "dict": (dict,),
}


@dataclass(frozen=True)
class Issue:
    line: int
    kind: str
    detail: str

    def __str__(self) -> str:
        return f"line {self.line}: {self.kind}: {self.detail}"


def _is_empty(value: object) -> bool:
    if value is None:
        return True
    if isinstance(value, (str, list, dict)) and len(value) == 0:
        return True
    return False


def validate_lines(
    lines: list[str],
    require: list[str] | None = None,
    types: dict[str, str] | None = None,
    unique: str | None = None,
    allow_blank: bool = True,
) -> list[Issue]:
    """Return every issue found. An empty list means the file is valid."""
    require = require or []
    types = types or {}
    issues: list[Issue] = []
    seen: dict[str, int] = {}

    for i, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        if not stripped:
            if not allow_blank:
                issues.append(Issue(i, "blank_line", "empty line not allowed"))
            continue

        try:
            record = json.loads(stripped)
        except json.JSONDecodeError as exc:
            issues.append(Issue(i, "invalid_json", exc.msg))
            continue

        if not isinstance(record, dict):
            issues.append(Issue(i, "not_an_object", f"got {type(record).__name__}"))
            continue

        for field in require:
            if field not in record:
                issues.append(Issue(i, "missing_field", field))
            elif _is_empty(record[field]):
                issues.append(Issue(i, "empty_field", field))

        for field, type_name in types.items():
            if field not in record:
                continue
            expected = _TYPE_ALIASES.get(type_name)
            if expected is None:
                issues.append(Issue(i, "unknown_type", f"{field}:{type_name}"))
                continue
            value = record[field]
            # bool is a subclass of int; keep them distinct unless bool is asked for.
            if isinstance(value, bool) and bool not in expected:
                issues.append(Issue(i, "wrong_type", f"{field} is bool, want {type_name}"))
            elif not isinstance(value, expected):
                issues.append(
                    Issue(i, "wrong_type", f"{field} is {type(value).__name__}, want {type_name}")
                )

        if unique and unique in record:
            key = json.dumps(record[unique], sort_keys=True)
            if key in seen:
                issues.append(
                    Issue(i, "duplicate_key", f"{unique}={record[unique]!r} first seen on line {seen[key]}")
                )
            else:
                seen[key] = i

    return issues


def _parse_types(spec: str | None) -> dict[str, str]:
    if not spec:
        return {}
    out = {}
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if ":" not in part:
            raise argparse.ArgumentTypeError(f"bad --types entry '{part}', expected field:type")
        field, type_name = part.split(":", 1)
        out[field.strip()] = type_name.strip()
    return out


def _parse_list(spec: str | None) -> list[str]:
    if not spec:
        return []
    return [p.strip() for p in spec.split(",") if p.strip()]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", help="path to a .jsonl file")
    ap.add_argument("--require", help="comma-separated fields that must be present and non-empty")
    ap.add_argument("--types", help="comma-separated field:type constraints (str,int,number,bool,list,object)")
    ap.add_argument("--unique", help="a field that must be unique across the file")
    ap.add_argument("--no-blank", action="store_true", help="treat blank lines as errors")
    ap.add_argument("--max-show", type=int, default=50, help="max issues to print")
    args = ap.parse_args(argv)

    try:
        with open(args.path, encoding="utf-8") as f:
            lines = f.readlines()
    except OSError as exc:
        print(f"cannot read {args.path}: {exc}", file=sys.stderr)
        return 2

    issues = validate_lines(
        lines,
        require=_parse_list(args.require),
        types=_parse_types(args.types),
        unique=args.unique,
        allow_blank=not args.no_blank,
    )

    non_blank = sum(1 for ln in lines if ln.strip())
    if not issues:
        print(f"OK: {non_blank} records valid in {args.path}")
        return 0

    for issue in issues[: args.max_show]:
        print(str(issue))
    if len(issues) > args.max_show:
        print(f"... and {len(issues) - args.max_show} more")
    print(f"FAIL: {len(issues)} issue(s) across {non_blank} records in {args.path}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
