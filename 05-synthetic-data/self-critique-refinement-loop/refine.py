"""A deterministic draft -> critique -> revise loop.

Self-refinement (draft, critique it, revise, repeat) is a common way to raise the
quality of generated data. This is a fully deterministic version so the loop's dynamics
are visible and testable: the critic checks a draft against a set of constraints and
lists violations; the reviser applies a targeted fix for each violation type; the loop
repeats until the critic is satisfied or a max-iteration cap is hit. It records the
trajectory so you can watch the violation count fall to zero.

The point is the *loop*, not the fixes — swap the critic/reviser for model calls and the
structure is unchanged.
"""
from __future__ import annotations

import re

_WORD = re.compile(r"\S+")


def critique(text: str, spec: dict) -> list[str]:
    """Return the list of violated constraints for a draft."""
    v: list[str] = []
    words = _WORD.findall(text)
    if "max_words" in spec and len(words) > spec["max_words"]:
        v.append("too_long")
    if spec.get("must_end_with_period") and not text.rstrip().endswith("."):
        v.append("no_end_period")
    if "  " in text:
        v.append("double_spaces")
    for kw in spec.get("must_include", []):
        if kw.lower() not in text.lower():
            v.append(f"missing:{kw}")
    if spec.get("no_trailing_space") and text != text.rstrip():
        v.append("trailing_space")
    return v


def revise(text: str, violations: list[str], spec: dict) -> str:
    """Apply targeted fixes for the reported violations.

    The tricky interaction is length vs required keywords: adding a keyword can push the
    text over the word limit, and a naive trim would drop the keyword right back off,
    causing the loop to oscillate. So the length trim is keyword-aware — it reserves room
    for required keywords and only ever trims non-keyword words."""
    required = spec.get("must_include", [])

    if "double_spaces" in violations:
        text = re.sub(r" {2,}", " ", text)

    for viol in violations:
        if viol.startswith("missing:"):
            text = f"{text.rstrip()} {viol.split(':', 1)[1]}"

    if "too_long" in violations and "max_words" in spec:
        kw_set = {k.lower() for k in required}
        words = _WORD.findall(text)
        keywords_in = [w for w in words if w.lower().strip(".") in kw_set]
        body = [w for w in words if w.lower().strip(".") not in kw_set]
        budget = max(0, spec["max_words"] - len(keywords_in))
        text = " ".join(body[:budget] + keywords_in)

    if "no_end_period" in violations:
        text = text.rstrip()
        if not text.endswith("."):
            text = text + "."

    if "trailing_space" in violations:
        text = text.rstrip()
    return text


def refine(draft: str, spec: dict, max_iters: int = 5) -> dict:
    """Run the loop, recording violations before each revision."""
    text = draft
    trajectory = []
    for _ in range(max_iters):
        viols = critique(text, spec)
        trajectory.append({"text": text, "violations": viols})
        if not viols:
            break
        text = revise(text, viols, spec)
    final_violations = critique(text, spec)
    return {
        "final_text": text,
        "iterations": len(trajectory),
        "converged": not final_violations,
        "final_violations": final_violations,
        "trajectory": trajectory,
    }
