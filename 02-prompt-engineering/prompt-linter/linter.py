"""A prompt quality linter.

Encodes prompt-engineering best practices as checks and flags common anti-patterns
in an instruction: no stated output format, undelimited input, vague quantifiers,
contradictory length constraints, structured output requested without an example,
and so on. Each finding has a severity and a human-readable message, and the prompt
gets a 0-100 score. It's a fully deterministic way to demonstrate what makes a prompt
good — as code, not prose.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

_TASK_VERBS = (
    "write", "summarize", "classify", "extract", "translate", "list", "explain",
    "generate", "answer", "analyze", "rewrite", "compare", "label", "score",
    "convert", "draft", "describe", "identify", "categorize",
)
_FORMAT_WORDS = ("json", "yaml", "csv", "table", "bullet", "list", "markdown", "format",
                 "respond with", "return", "output", "schema")
_BREVITY = ("brief", "short", "concise", "one sentence", "few words", "terse")
_THOROUGH = ("comprehensive", "detailed", "thorough", "exhaustive", "in depth", "in-depth", "as much detail")
_VAGUE = ("some", "a few", "several", "many", "appropriate", "as needed", "etc.", "and so on", "relevant")
_STRUCTURED = ("json", "yaml", "table", "csv", "schema")


@dataclass(frozen=True)
class Issue:
    rule: str
    severity: str  # "high" | "medium" | "low"
    message: str


_SEVERITY_PENALTY = {"high": 25, "medium": 12, "low": 5}


def _has_any(text: str, needles) -> bool:
    # Match at a word start (so "format" does not match "information") while allowing
    # inflected endings (so "comprehensive" still matches "comprehensively"). Phrases
    # or tokens with punctuation fall back to a plain substring check.
    for n in needles:
        if re.search(r"[^\w]", n):
            if n in text:
                return True
        elif re.search(rf"\b{re.escape(n)}", text):
            return True
    return False


def lint(prompt: str) -> dict:
    low = prompt.lower()
    words = prompt.split()
    issues: list[Issue] = []

    if not _has_any(low, _FORMAT_WORDS):
        issues.append(Issue("no_output_format", "high", "No output format is specified; say exactly what to return."))

    mentions_input = _has_any(low, ("the text", "the following", "this document", "the input", "the passage", "below"))
    has_delims = bool(re.search(r"```|<[a-z_]+>|\"\"\"|'''", prompt)) or '"' in prompt
    if mentions_input and not has_delims:
        issues.append(Issue(
            "undelimited_input", "medium",
            "Input is referenced but not delimited; wrap it in triple backticks or tags.",
        ))

    if _has_any(low, _BREVITY) and _has_any(low, _THOROUGH):
        issues.append(Issue("conflicting_length", "high", "Prompt asks to be both brief and comprehensive; pick one."))

    vague_hits = [v for v in _VAGUE if re.search(rf"\b{re.escape(v)}", low)]
    if vague_hits:
        issues.append(Issue(
            "vague_quantifier", "medium",
            f"Vague wording ({', '.join(vague_hits)}); be specific with numbers.",
        ))

    if not _has_any(low, _TASK_VERBS):
        issues.append(Issue(
            "unclear_task", "high",
            "No clear task verb; start with an imperative like 'Summarize' or 'Classify'.",
        ))

    if _has_any(low, _STRUCTURED) and not _has_any(low, ("example", "e.g.", "for instance", "{")):
        issues.append(Issue(
            "no_example_for_structure", "medium",
            "Structured output requested without an example; show one.",
        ))

    if _has_any(low, ("please", "thank you", "could you", "would you", "kindly")):
        issues.append(Issue("politeness_filler", "low", "Politeness filler adds noise; instructions can be direct."))

    if len(words) > 250:
        issues.append(Issue("too_long", "low", f"Prompt is long ({len(words)} words); consider tightening."))

    caps = [w for w in words if len(w) > 3 and w.isupper()]
    if len(caps) >= 4:
        issues.append(Issue("shouting", "low", "Heavy ALL-CAPS emphasis; use it sparingly."))

    penalty = sum(_SEVERITY_PENALTY[i.severity] for i in issues)
    score = max(0, 100 - penalty)
    return {
        "score": score,
        "issues": [{"rule": i.rule, "severity": i.severity, "message": i.message} for i in issues],
    }
