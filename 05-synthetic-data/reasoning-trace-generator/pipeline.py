"""Generate verified reasoning traces via rejection sampling.

The generator produces candidate (question, step-by-step reasoning, answer)
records for four problem types. Because each problem is templated from known
parameters, a *separate* reference implementation can recompute the correct
answer and reject any trace whose stated answer is wrong. A little noise is
injected on purpose so the verifier has something to catch, exactly like
filtering real, imperfect model generations down to a clean training set.

Pipeline: generate -> deduplicate -> drop too-short traces -> keep only traces
whose answer the independent reference confirms.
"""
from __future__ import annotations

import math
import random

# Defaults shared by the CLI and the tests so committed results are reproducible.
N = 200
SEED = 7
FLAW_RATE = 0.15
MIN_STEPS = 2
TOL = 0.011

_NAMES = ["Maria", "Sam", "Priya", "Diego", "Aisha", "Noah", "Lena", "Omar"]


# --- generators (each returns a complete, correct record) ----------------------


def make_arithmetic(rng: random.Random) -> dict:
    name = rng.choice(_NAMES)
    x, z = rng.randint(20, 60), rng.randint(1, 20)
    y = rng.randint(1, x)
    ans = x - y + z
    return {
        "type": "arithmetic",
        "question": f"{name} had {x} apples, gave away {y}, then bought {z} more. How many now?",
        "params": {"x": x, "y": y, "z": z},
        "reasoning": [
            f"Start with {x}.",
            f"Give away {y}: {x} - {y} = {x - y}.",
            f"Buy {z} more: {x - y} + {z} = {ans}.",
        ],
        "answer_value": ans,
    }


def make_percentage(rng: random.Random) -> dict:
    price = rng.randint(20, 200)
    pct = rng.choice([10, 15, 20, 25, 30, 40, 50])
    discount = round(price * pct / 100, 2)
    sale = round(price - discount, 2)
    return {
        "type": "percentage",
        "question": f"A jacket costs ${price}. It is {pct}% off. What is the sale price?",
        "params": {"price": price, "pct": pct},
        "reasoning": [
            f"Discount = {pct}% of {price} = {discount}.",
            f"Sale price = {price} - {discount} = {sale}.",
        ],
        "answer_value": sale,
    }


def make_conversion(rng: random.Random) -> dict:
    km = rng.randint(1, 100)
    m = km * 1000
    return {
        "type": "conversion",
        "question": f"Convert {km} kilometers to meters.",
        "params": {"km": km},
        "reasoning": ["1 km = 1000 m.", f"{km} km = {km} * 1000 = {m} m."],
        "answer_value": m,
    }


def make_gcd(rng: random.Random) -> dict:
    a, b = rng.randint(2, 100), rng.randint(2, 100)
    g = math.gcd(a, b)
    return {
        "type": "gcd",
        "question": f"What is the greatest common divisor of {a} and {b}?",
        "params": {"a": a, "b": b},
        "reasoning": [f"List shared factors of {a} and {b}.", f"GCD({a}, {b}) = {g}."],
        "answer_value": g,
    }


_MAKERS = [make_arithmetic, make_percentage, make_conversion, make_gcd]


def generate(n: int, seed: int, flaw_rate: float) -> list[dict]:
    rng = random.Random(seed)
    records = []
    for i in range(n):
        rec = _MAKERS[i % len(_MAKERS)](rng)
        rec["id"] = f"{rec['type']}-{i:04d}"
        if rng.random() < flaw_rate:  # corrupt the stated answer, keep params honest
            rec["answer_value"] = round(rec["answer_value"] + rng.choice([-2, -1, 1, 2]), 2)
        records.append(rec)
    return records


# --- independent reference (the verifier does not trust the generator) ----------


def expected_answer(record: dict) -> float:
    t, p = record["type"], record["params"]
    if t == "arithmetic":
        return p["x"] - p["y"] + p["z"]
    if t == "percentage":
        return round(p["price"] - round(p["price"] * p["pct"] / 100, 2), 2)
    if t == "conversion":
        return p["km"] * 1000
    if t == "gcd":
        return math.gcd(p["a"], p["b"])
    raise ValueError(f"unknown problem type: {t}")


def is_correct(record: dict, tol: float = TOL) -> bool:
    return abs(record["answer_value"] - expected_answer(record)) <= tol


def _normalize(question: str) -> str:
    return " ".join(question.lower().split())


# --- pipeline ------------------------------------------------------------------


def run_pipeline(
    n: int = N, seed: int = SEED, flaw_rate: float = FLAW_RATE, min_steps: int = MIN_STEPS
) -> tuple[list[dict], dict]:
    records = generate(n, seed, flaw_rate)

    seen: set[str] = set()
    deduped, n_dup = [], 0
    for r in records:
        key = _normalize(r["question"])
        if key in seen:
            n_dup += 1
            continue
        seen.add(key)
        deduped.append(r)

    accepted, n_short, n_wrong = [], 0, 0
    for r in deduped:
        if len(r["reasoning"]) < min_steps:
            n_short += 1
        elif not is_correct(r):
            n_wrong += 1
        else:
            accepted.append(r)

    stats = {
        "generated": n,
        "duplicates_removed": n_dup,
        "rejected_short": n_short,
        "rejected_wrong_answer": n_wrong,
        "accepted": len(accepted),
        "acceptance_rate": round(len(accepted) / n, 4) if n else 0.0,
    }
    return accepted, stats
