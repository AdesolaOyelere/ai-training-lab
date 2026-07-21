"""Turn a metrics JSON file into a readable Markdown report.

Every eval in this repo writes a results.json; turning those into a shareable report by
hand is tedious. This tool renders a JSON object into Markdown: scalar fields become a
key/value table, a list of uniform dicts becomes a table with a column per key, and
nested objects are flattened with dotted keys. It's a small, general reporting utility.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _fmt(value: object) -> str:
    if isinstance(value, float):
        return f"{value:.4g}"
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value).replace("|", "\\|").replace("\n", " ")


def _flatten(obj: dict, prefix: str = "") -> dict:
    flat: dict[str, object] = {}
    for k, v in obj.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            flat.update(_flatten(v, prefix=f"{key}."))
        else:
            flat[key] = v
    return flat


def _list_of_dicts_table(rows: list[dict]) -> list[str]:
    columns: list[str] = []
    for row in rows:
        for k in row:
            if k not in columns:
                columns.append(k)
    lines = ["| " + " | ".join(columns) + " |", "|" + "|".join(["---"] * len(columns)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(_fmt(row.get(c, "")) for c in columns) + " |")
    return lines


def render(data: dict, title: str = "Report") -> str:
    scalars: dict[str, object] = {}
    tables: list[tuple[str, list[str]]] = []

    for key, value in data.items():
        if isinstance(value, list) and value and all(isinstance(x, dict) for x in value):
            tables.append((key, _list_of_dicts_table(value)))
        elif isinstance(value, dict):
            scalars.update(_flatten({key: value}))
        elif isinstance(value, list):
            scalars[key] = ", ".join(_fmt(x) for x in value)
        else:
            scalars[key] = value

    out = [f"# {title}", ""]
    if scalars:
        out += ["| Metric | Value |", "|---|---|"]
        out += [f"| {k} | {_fmt(v)} |" for k, v in scalars.items()]
        out.append("")
    for name, table in tables:
        out.append(f"## {name}")
        out += table
        out.append("")
    return "\n".join(out).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("path", help="a results .json file")
    ap.add_argument("--title", default="Report")
    ap.add_argument("-o", "--out", help="output .md (default: stdout)")
    args = ap.parse_args(argv)

    data = json.loads(Path(args.path).read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        print("top-level JSON must be an object", file=sys.stderr)
        return 1
    md = render(data, args.title)
    if args.out:
        Path(args.out).write_text(md, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
