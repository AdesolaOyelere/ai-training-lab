"""Tests for the token/cost estimator: empty/simple counts, long-word splitting,
exact cost math, dataset sizing over the sample, and CLI exit."""
import json
from pathlib import Path

import pytest
from token_counter import analyze_dataset, estimate_cost, estimate_tokens, main

HERE = Path(__file__).resolve().parent.parent


def test_empty_and_simple():
    assert estimate_tokens("") == 0
    assert estimate_tokens("hello world") == 3          # 11 chars, ceil(11/4)
    assert estimate_tokens("cat") == 1                  # 3 chars, ceil(3/4)


def test_scales_with_length():
    # ~4 characters per token
    assert estimate_tokens("internationalization") == 5   # 20 chars / 4
    assert estimate_tokens("a" * 400) == 100


def test_cost_math_is_exact():
    # 1,000,000 input tokens at sonnet's $3/M = exactly $3.00
    assert estimate_cost(1_000_000, 0, "sonnet") == 3.0
    # 1M output tokens at $15/M = $15.00
    assert estimate_cost(0, 1_000_000, "sonnet") == 15.0
    assert estimate_cost(500_000, 500_000, "haiku") == round(0.4 + 2.0, 6)


def test_unknown_model_raises():
    with pytest.raises(ValueError):
        estimate_cost(1, 1, "nope")


def test_dataset_sizing():
    rows = [json.loads(x) for x in (HERE / "sample_data" / "dataset.jsonl").read_text().splitlines() if x.strip()]
    stats = analyze_dataset(rows, ["prompt", "response"], "sonnet")
    assert stats["n_rows"] == 3
    assert stats["input_tokens"] > 0
    # cost equals tokens/1e6 * $3, recomputed independently
    assert stats["estimated_input_cost_usd"] == round(stats["input_tokens"] / 1_000_000 * 3.0, 6)


def test_cli_text_mode():
    assert main(["--text", "hello world", "--model", "haiku"]) == 0
