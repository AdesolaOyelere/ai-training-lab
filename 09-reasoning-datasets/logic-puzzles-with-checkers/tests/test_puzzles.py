"""Tests for the puzzles and their checkers: each puzzle has a unique solution, the
checker accepts it and rejects wrong candidates, and the checkers really enforce every
stated constraint (so they can grade model solutions by correctness)."""
from puzzles import (
    check,
    solve_knights_knaves,
    solve_numbers,
    solve_seating,
    unique_solution,
)


def test_each_puzzle_has_unique_solution():
    assert len(solve_seating()) == 1
    assert len(solve_numbers()) == 1
    assert len(solve_knights_knaves()) == 1


def test_seating_checker():
    assert unique_solution("seating") == ["A", "D", "C", "B"]
    assert check("seating", ["A", "D", "C", "B"])
    assert not check("seating", ["B", "A", "C", "D"])   # A must be left of B, D right of A


def test_numbers_checker():
    sol = unique_solution("numbers")
    assert check("numbers", sol)
    # violate the "y is even" rule
    assert not check("numbers", {"w": 1, "x": 4, "y": 3, "z": 2})
    # not a permutation of 1..4
    assert not check("numbers", {"w": 1, "x": 1, "y": 2, "z": 3})


def test_knights_knaves_checker():
    # A says "we are both knaves" -> A is a knave, B is a knight
    assert unique_solution("knights_knaves") == (False, True)
    assert check("knights_knaves", (False, True))
    assert not check("knights_knaves", (True, True))


def test_unknown_puzzle_raises():
    try:
        check("nope", None)
        raise AssertionError("expected KeyError")
    except KeyError:
        pass
