"""Tests for the JSON-to-Markdown renderer: scalars become a key/value table, nested
objects flatten with dotted keys, a list of dicts becomes a column table, pipes are
escaped, and the CLI writes a file."""
import json
from pathlib import Path

from to_markdown import main, render

HERE = Path(__file__).resolve().parent.parent


def test_scalars_and_nested_flatten():
    md = render({"n": 3, "rate": 0.5, "confusion": {"tp": 2, "fp": 1}}, title="T")
    assert "# T" in md
    assert "| n | 3 |" in md
    assert "| confusion.tp | 2 |" in md          # nested flattened with dotted key
    assert "| rate | 0.5 |" in md


def test_list_of_dicts_becomes_table():
    md = render({"per_item": [{"id": "a", "score": 1.0}, {"id": "b", "score": 0.5}]})
    assert "## per_item" in md
    assert "| id | score |" in md
    assert "| a | 1 |" in md


def test_scalar_list_is_joined():
    md = render({"tags": ["x", "y", "z"]})
    assert "| tags | x, y, z |" in md


def test_pipe_is_escaped():
    md = render({"note": "a | b"})
    assert "a \\| b" in md


def test_cli_writes_file(tmp_path):
    out = tmp_path / "r.md"
    rc = main([str(HERE / "sample_data" / "results.json"), "--title", "Eval", "-o", str(out)])
    assert rc == 0
    text = out.read_text(encoding="utf-8")
    assert "# Eval" in text
    assert "## per_item" in text
    # sanity: the committed data has 8 items and a confusion sub-table flattened
    data = json.loads((HERE / "sample_data" / "results.json").read_text())
    assert data["n_items"] == 8
