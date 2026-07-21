"""Pairwise LLM-as-judge harness with position-bias control.

Using a model to judge which of two responses is better is standard practice, but
judges have a well-known flaw: they favor whichever answer is shown first
(position bias). The fix used in serious evaluations is to judge each pair twice,
swapping the order, and only count a win when the judge is consistent both ways;
disagreement is scored as a tie. This harness implements that protocol and rolls the
results up into win rates plus a measured position-bias rate.

The judge sits behind a swappable interface: a deterministic mock drives the tests
and committed results; a real model can be dropped in unchanged.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

# A judge takes (question, answer_A, answer_B) and returns "A", "B", or "tie".
Judge = Callable[[str, str, str], str]


@dataclass
class Pair:
    id: str
    question: str
    answer_a: str  # the response from model "a"
    answer_b: str  # the response from model "b"


def judge_pair_debiased(pair: Pair, judge: Judge) -> dict:
    """Judge a pair in both orders; a real win requires agreement across orders."""
    # Order 1: a shown first (as "A"), b shown second (as "B")
    v1 = judge(pair.question, pair.answer_a, pair.answer_b)
    # Order 2: b shown first (as "A"), a shown second (as "B")
    v2 = judge(pair.question, pair.answer_b, pair.answer_a)

    # Translate each verdict back to which model (a/b) it favored.
    first = {"A": "a", "B": "b", "tie": "tie"}[v1]
    second = {"A": "b", "B": "a", "tie": "tie"}[v2]

    if first == second and first != "tie":
        winner = first
        consistent = True
    else:
        winner = "tie"
        consistent = first == second  # tie==tie is consistent; a-vs-b flip is position bias
    return {
        "id": pair.id,
        "winner": winner,
        "consistent": consistent,
        "order1_favored": first,
        "order2_favored": second,
        "position_bias": (first != second) and "tie" not in (first, second),
    }


def run_judgements(pairs: list[Pair], judge: Judge) -> dict:
    results = [judge_pair_debiased(p, judge) for p in pairs]
    n = len(results)
    a_wins = sum(1 for r in results if r["winner"] == "a")
    b_wins = sum(1 for r in results if r["winner"] == "b")
    ties = sum(1 for r in results if r["winner"] == "tie")
    biased = sum(1 for r in results if r["position_bias"])
    return {
        "n": n,
        "a_win_rate": round(a_wins / n, 4) if n else 0.0,
        "b_win_rate": round(b_wins / n, 4) if n else 0.0,
        "tie_rate": round(ties / n, 4) if n else 0.0,
        "position_bias_rate": round(biased / n, 4) if n else 0.0,
        "results": results,
    }


def first_position_judge(prefers: dict[str, str]) -> Judge:
    """A mock judge that is right when it agrees across orders but exhibits position
    bias on the pairs named in `prefers` (mapping pair-question -> always "A").

    For pairs not listed, it favors the answer containing the token 'BETTER',
    consistently regardless of order (a well-behaved judge)."""

    def judge(question: str, ans_first: str, ans_second: str) -> str:
        if question in prefers:
            return "A"  # always picks whatever is shown first -> position bias
        if "BETTER" in ans_first and "BETTER" not in ans_second:
            return "A"
        if "BETTER" in ans_second and "BETTER" not in ans_first:
            return "B"
        return "tie"

    return judge
