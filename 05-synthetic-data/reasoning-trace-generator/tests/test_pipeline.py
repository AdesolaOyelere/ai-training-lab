"""Tests for the reasoning-trace pipeline.

The important guarantees: the independent reference agrees with clean generation,
the verifier actually rejects wrong answers, dedup and the whole pipeline are
deterministic, and every accepted record is verifiably correct and unique. A final
test pins the committed report so the sample stays honest.
"""
import json
from pathlib import Path

from pipeline import (
    FLAW_RATE,
    MIN_STEPS,
    SEED,
    N,
    expected_answer,
    generate,
    is_correct,
    run_pipeline,
)

HERE = Path(__file__).resolve().parent.parent


def test_clean_generation_is_all_correct():
    # With no injected flaws, the independent reference must confirm every record.
    for rec in generate(200, seed=1, flaw_rate=0.0):
        assert is_correct(rec), rec
        assert rec["answer_value"] == expected_answer(rec)


def test_verifier_rejects_a_wrong_answer():
    rec = generate(1, seed=1, flaw_rate=0.0)[0]
    rec["answer_value"] = rec["answer_value"] + 5
    assert not is_correct(rec)


def test_pipeline_is_deterministic():
    a1, s1 = run_pipeline(120, seed=42, flaw_rate=0.2)
    a2, s2 = run_pipeline(120, seed=42, flaw_rate=0.2)
    assert s1 == s2
    assert [r["id"] for r in a1] == [r["id"] for r in a2]


def test_flaws_are_caught_and_accepted_set_is_clean():
    accepted, stats = run_pipeline(200, seed=7, flaw_rate=0.2)
    # some wrong answers were injected, so some must be rejected
    assert stats["rejected_wrong_answer"] > 0
    assert 0.0 < stats["acceptance_rate"] < 1.0
    # everything that survived is correct and unique
    assert all(is_correct(r) for r in accepted)
    questions = [" ".join(r["question"].lower().split()) for r in accepted]
    assert len(questions) == len(set(questions))
    # bookkeeping adds up
    assert (
        stats["accepted"] + stats["rejected_wrong_answer"] + stats["rejected_short"]
        == stats["generated"] - stats["duplicates_removed"]
    )


def test_committed_report_matches_fresh_run():
    committed = json.loads((HERE / "results" / "report.json").read_text(encoding="utf-8"))
    _, stats = run_pipeline(N, SEED, FLAW_RATE, MIN_STEPS)
    assert committed == stats
