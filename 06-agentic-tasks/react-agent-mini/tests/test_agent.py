"""Tests for the ReAct loop: the tools work and are safe, the loop records a proper
trace, the max-steps guard and unknown-tool guard fire, and the rule-based policy
answers tool-requiring questions correctly end to end."""
from agent import (
    Trace,
    rule_based_policy,
    run,
    tool_calculator,
    tool_lookup,
    tool_wordcount,
)


def test_tools():
    assert tool_calculator("12 * (3 + 4)") == "84"
    assert tool_calculator("10 / 4") == "2.5"
    assert tool_calculator("2 ** 10") == "1024"
    assert tool_lookup("capital of France") == "Paris"
    assert tool_lookup("nonexistent") == "unknown"
    assert tool_wordcount("one two three") == "3"


def test_calculator_is_safe():
    # arbitrary code must not execute; it should be rejected, not evaluated
    assert tool_calculator("__import__('os').system('echo hi')").startswith("error")


def test_full_loop_math_question():
    trace = run("What is 12 * (3 + 4)?", rule_based_policy)
    assert trace.answer == "84"
    assert trace.stopped_reason == "answered"
    # exactly one tool step (calculator) then a finish
    assert len(trace.steps) == 1
    assert trace.steps[0].action == "calculator"


def test_full_loop_lookup_question():
    trace = run("What is the capital of France?", rule_based_policy)
    assert trace.answer == "Paris"
    assert trace.steps[0].action == "lookup"


def test_unknown_question_finishes_without_tool():
    trace = run("What is the meaning of life?", rule_based_policy)
    assert trace.answer == "I don't know"
    assert trace.steps == []


def test_max_steps_guard():
    # a policy that never finishes must be stopped by the step cap
    def loop_forever(q: str, t: Trace):
        return "action", "wordcount", "hello world"

    trace = run("x", loop_forever, max_steps=3)
    assert trace.stopped_reason == "max_steps"
    assert len(trace.steps) == 3


def test_invalid_tool_guard():
    def bad(q: str, t: Trace):
        return "action", "does_not_exist", ""

    trace = run("x", bad)
    assert trace.stopped_reason == "invalid tool"
