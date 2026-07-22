"""Tests for the few-shot ablation: zero-shot falls back to the prior, more exemplars
help, the curve is non-decreasing, and the committed result is pinned."""
import json
from pathlib import Path

from ablation import classify, run_ablation
from data import TEST, TRAIN

HERE = Path(__file__).resolve().parent.parent


def test_zero_shot_uses_prior():
    assert classify("anything at all", [], "greeting") == "greeting"


def test_nearest_exemplar_classifies():
    exemplars = [{"text": "hello hi", "label": "greeting"}, {"text": "rain sun", "label": "weather"}]
    assert classify("hello there", exemplars, "weather") == "greeting"
    assert classify("will it rain", exemplars, "greeting") == "weather"


def test_more_shots_help_and_curve_is_monotonic():
    result = run_ablation(TRAIN, TEST, shots=[0, 3, 9])
    accs = [c["accuracy"] for c in result["conditions"]]
    assert accs[0] < accs[-1]                 # few-shot beats zero-shot
    assert result["monotonic_nondecreasing"]
    assert result["improvement_0_to_max"] > 0


def test_pins_committed_results():
    result = run_ablation(TRAIN, TEST, shots=[0, 1, 3, 6, 9])
    committed = json.loads((HERE / "results" / "results.json").read_text(encoding="utf-8"))
    assert committed == result
    # zero-shot can only get the prior class right; full-shot should be perfect here
    assert result["conditions"][0]["accuracy"] < 1.0
    assert result["conditions"][-1]["accuracy"] == 1.0
