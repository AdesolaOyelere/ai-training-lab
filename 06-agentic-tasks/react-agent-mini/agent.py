"""A minimal ReAct-style agent loop over mock tools.

ReAct interleaves reasoning and acting: the agent emits a thought, takes an action
(a tool call), observes the result, and repeats until it can answer. This implements
that loop with a pluggable policy and a real tool registry, and records the full
trace so it can be inspected or scored. The default policy is a deterministic
rule-based stand-in for a model, which keeps the whole thing testable and offline; a
real model policy drops into the same interface.

Tools: calculator (arithmetic), lookup (a tiny knowledge base), wordcount.
"""
from __future__ import annotations

import ast
import operator
import re
from collections.abc import Callable
from dataclasses import dataclass, field

# --- tools ---------------------------------------------------------------------

_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg,
    ast.Mod: operator.mod,
}

_FACTS = {
    "capital of france": "Paris",
    "capital of japan": "Tokyo",
    "speed of light": "299792458 m/s",
    "largest planet": "Jupiter",
}


def _safe_eval(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("unsupported expression")


def tool_calculator(arg: str) -> str:
    try:
        result = _safe_eval(ast.parse(arg, mode="eval"))
    except (ValueError, SyntaxError, ZeroDivisionError) as exc:
        return f"error: {exc}"
    return str(int(result) if isinstance(result, float) and result.is_integer() else result)


def tool_lookup(arg: str) -> str:
    return _FACTS.get(arg.strip().lower(), "unknown")


def tool_wordcount(arg: str) -> str:
    return str(len(re.findall(r"\w+", arg)))


TOOLS: dict[str, Callable[[str], str]] = {
    "calculator": tool_calculator,
    "lookup": tool_lookup,
    "wordcount": tool_wordcount,
}


# --- loop ----------------------------------------------------------------------


@dataclass
class Step:
    thought: str
    action: str | None
    action_input: str | None
    observation: str | None


@dataclass
class Trace:
    question: str
    steps: list[Step] = field(default_factory=list)
    answer: str | None = None
    stopped_reason: str = ""

    def as_dict(self) -> dict:
        return {
            "question": self.question,
            "answer": self.answer,
            "stopped_reason": self.stopped_reason,
            "steps": [vars(s) for s in self.steps],
        }


# A policy inspects the question and the trace so far and returns the next move:
# either ("action", tool, input) or ("finish", answer, "").
Policy = Callable[[str, Trace], tuple[str, str, str]]


def run(question: str, policy: Policy, max_steps: int = 5) -> Trace:
    trace = Trace(question=question)
    for _ in range(max_steps):
        kind, a, b = policy(question, trace)
        if kind == "finish":
            trace.answer = a
            trace.stopped_reason = "answered"
            return trace
        if a not in TOOLS:
            trace.steps.append(Step(f"tried unknown tool {a}", a, b, "error: no such tool"))
            trace.stopped_reason = "invalid tool"
            return trace
        obs = TOOLS[a](b)
        trace.steps.append(Step(f"use {a}", a, b, obs))
    trace.stopped_reason = "max_steps"
    return trace


def rule_based_policy(question: str, trace: Trace) -> tuple[str, str, str]:
    """A deterministic stand-in for a model policy.

    Decides which tool to use from the question, then answers using the observation
    from the previous step. Good enough to exercise the full ReAct loop offline."""
    q = question.lower().strip()

    # If we already have an observation, produce the final answer from it.
    if trace.steps:
        last = trace.steps[-1]
        return "finish", last.observation or "unknown", ""

    if any(w in q for w in ("what is", "calculate", "compute")) and re.search(r"\d", q):
        expr = re.sub(r"[^0-9+\-*/(). ]", "", question).strip()
        if re.search(r"\d", expr) and re.search(r"[-+*/]", expr):
            return "action", "calculator", expr
    if q.startswith(("who", "what")) and ("capital" in q or "planet" in q or "speed of light" in q):
        key = re.sub(r"^(what is|who is)\s+(the\s+)?", "", q).rstrip("?").strip()
        return "action", "lookup", key
    if "how many words" in q:
        payload = question.split(":", 1)[1] if ":" in question else question
        return "action", "wordcount", payload
    return "finish", "I don't know", ""
