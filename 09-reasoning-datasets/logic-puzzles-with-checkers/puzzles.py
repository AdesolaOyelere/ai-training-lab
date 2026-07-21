"""Logic puzzles paired with programmatic checkers.

A reasoning dataset is far more useful when each item ships with a verifier that can
confirm a proposed solution, rather than only a stored answer string. This module
defines a few constraint-style puzzles, each with (a) a generator that can produce the
puzzle and its unique solution and (b) a checker that validates any candidate solution
against the puzzle's rules. That lets you grade model solutions by *correctness*, not
string match, and even accept alternative valid answers.
"""
from __future__ import annotations

from itertools import permutations

# --- puzzle 1: seating -----------------------------------------------------------
# Four people (A, B, C, D) sit in a row of seats 1..4 under constraints.


def seating_constraints(order: list[str]) -> bool:
    pos = {name: i for i, name in enumerate(order)}
    # A is somewhere to the left of B; C is not at either end; D is immediately right of A
    return (
        pos["A"] < pos["B"]
        and 0 < pos["C"] < 3
        and pos["D"] == pos["A"] + 1
    )


def solve_seating() -> list[list[str]]:
    return [list(p) for p in permutations("ABCD") if seating_constraints(list(p))]


# --- puzzle 2: number placement (mini) -------------------------------------------
# Place 1..4 in cells w,x,y,z so that: w+x == y+z, w < z, and y is even.


def number_constraints(assignment: dict[str, int]) -> bool:
    if sorted(assignment.values()) != [1, 2, 3, 4]:
        return False
    w, x, y, z = assignment["w"], assignment["x"], assignment["y"], assignment["z"]
    return (w + x == y + z) and (w < z) and (y % 2 == 0)


def solve_numbers() -> list[dict[str, int]]:
    solutions = []
    for perm in permutations([1, 2, 3, 4]):
        a = dict(zip("wxyz", perm, strict=True))
        if number_constraints(a):
            solutions.append(a)
    return solutions


# --- puzzle 3: knights and knaves -----------------------------------------------
# Two islanders. A says: "We are both knaves." Knights always tell the truth; knaves
# always lie. Determine who is a knight (True) and who is a knave (False).


def kk_consistent(a_is_knight: bool, b_is_knight: bool) -> bool:
    # A's statement is "both are knaves" == (not A_knight and not B_knight)
    statement = (not a_is_knight) and (not b_is_knight)
    # A is a knight iff A's statement is true; a knave iff it is false.
    return a_is_knight == statement


def solve_knights_knaves() -> list[tuple[bool, bool]]:
    return [(a, b) for a in (True, False) for b in (True, False) if kk_consistent(a, b)]


PUZZLES = {
    "seating": {"checker": seating_constraints, "solver": solve_seating},
    "numbers": {"checker": number_constraints, "solver": solve_numbers},
    "knights_knaves": {"checker": lambda s: kk_consistent(*s), "solver": solve_knights_knaves},
}


def check(name: str, candidate) -> bool:
    if name not in PUZZLES:
        raise KeyError(f"unknown puzzle: {name}")
    return bool(PUZZLES[name]["checker"](candidate))


def unique_solution(name: str):
    sols = PUZZLES[name]["solver"]()
    return sols[0] if len(sols) == 1 else None
