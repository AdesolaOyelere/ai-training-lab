#!/usr/bin/env python3
"""Render the sample results.json to Markdown and save it.

    python run.py
"""
from __future__ import annotations

import json
from pathlib import Path

from to_markdown import render

HERE = Path(__file__).parent


def main() -> int:
    data = json.loads((HERE / "sample_data" / "results.json").read_text(encoding="utf-8"))
    md = render(data, title="Eval Results")

    out = HERE / "results"
    out.mkdir(exist_ok=True)
    (out / "report.md").write_text(md, encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
