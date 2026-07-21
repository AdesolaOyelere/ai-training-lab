"""A graded math word-problem dataset with a robust answer checker.

A reasoning dataset is only useful if you can grade answers automatically and
fairly. Exact string match is too strict — "1,200", "1200", "1200.0", and
"$1200" are the same number; "yes." and "Yes" are the same label. This module
extracts the final answer from free-form model output and compares it to the gold
answer by type (number, fraction, or short text), then scores a whole dataset.
"""
from __future__ import annotations

import re
from fractions import Fraction

_NUM = re.compile(r"-?\$?\d[\d,]*(?:\.\d+)?")
_FINAL_MARKERS = ("final answer", "answer:", "the answer is", "=", "therefore", "so,")


def parse_number(text: str) -> float | None:
    """Pull the last number out of text, tolerating $, commas, and decimals."""
    matches = _NUM.findall(text)
    if not matches:
        return None
    raw = matches[-1].replace(",", "").replace("$", "")
    try:
        return float(raw)
    except ValueError:
        return None


def _last_line_after_marker(output: str) -> str:
    low = output.lower()
    best = -1
    for m in _FINAL_MARKERS:
        idx = low.rfind(m)
        if idx > best:
            best = idx + len(m)
    return output[best:] if best >= 0 else output


def check_numeric(output: str, gold: float, tol: float = 1e-6) -> bool:
    got = parse_number(_last_line_after_marker(output))
    if got is None:
        got = parse_number(output)
    return got is not None and abs(got - gold) <= tol


def check_fraction(output: str, gold: str) -> bool:
    gold_frac = Fraction(gold)
    tail = _last_line_after_marker(output)
    for token in re.findall(r"-?\d+\s*/\s*-?\d+|-?\d+\.\d+|-?\d+", tail) or []:
        try:
            if Fraction(token.replace(" ", "")) == gold_frac:
                return True
        except (ValueError, ZeroDivisionError):
            continue
    return False


def check_text(output: str, gold: str) -> bool:
    def norm(s: str) -> str:
        return re.sub(r"[^\w\s]", "", s).strip().lower()

    tail = norm(_last_line_after_marker(output))
    return norm(gold) in tail if tail else False


def grade_answer(output: str, gold: str, answer_type: str) -> bool:
    if answer_type == "number":
        return check_numeric(output, float(gold))
    if answer_type == "fraction":
        return check_fraction(output, gold)
    if answer_type == "text":
        return check_text(output, gold)
    raise ValueError(f"unknown answer_type: {answer_type}")


def grade_dataset(items: list[dict], answers: dict[str, str]) -> dict:
    """items: [{id, question, answer, answer_type}]; answers: {id: model_output}."""
    per_item, correct = [], 0
    by_type: dict[str, list[int]] = {}
    for it in items:
        output = answers.get(it["id"], "")
        ok = grade_answer(output, it["answer"], it["answer_type"])
        correct += ok
        per_item.append({"id": it["id"], "answer_type": it["answer_type"], "correct": ok})
        by_type.setdefault(it["answer_type"], []).append(int(ok))
    n = len(items)
    return {
        "n": n,
        "accuracy": round(correct / n, 4) if n else 0.0,
        "accuracy_by_type": {t: round(sum(v) / len(v), 4) for t, v in by_type.items()},
        "per_item": per_item,
    }
