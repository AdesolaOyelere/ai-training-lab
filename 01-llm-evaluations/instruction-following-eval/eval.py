"""Instruction-following eval with programmatically verifiable constraints.

Each eval item pairs a prompt with a list of constraints that can be checked
deterministically against a model's output (word counts, required substrings,
valid JSON, and so on). The score is the fraction of constraints satisfied, plus
a stricter "perfect" rate for items where every constraint passes.

This mirrors the design of verifiable instruction-following benchmarks: no
LLM-as-judge, no subjectivity, so the grader is exact and cheap to run.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Callable

# --- constraint checkers -------------------------------------------------------
# Each checker takes the model output text plus the constraint params and returns
# True when the output satisfies the constraint.

_SENTENCE_SPLIT = re.compile(r"[.!?]+(?:\s|$)")
_WORD = re.compile(r"\b[\w']+\b")


def _words(text: str) -> list[str]:
    return _WORD.findall(text)


def check_word_count_max(text: str, p: dict) -> bool:
    return len(_words(text)) <= int(p["n"])


def check_word_count_min(text: str, p: dict) -> bool:
    return len(_words(text)) >= int(p["n"])


def check_must_include_all(text: str, p: dict) -> bool:
    hay = text if p.get("case_sensitive") else text.lower()
    subs = p["substrings"] if p.get("case_sensitive") else [s.lower() for s in p["substrings"]]
    return all(s in hay for s in subs)


def check_must_not_include(text: str, p: dict) -> bool:
    hay = text if p.get("case_sensitive") else text.lower()
    subs = p["substrings"] if p.get("case_sensitive") else [s.lower() for s in p["substrings"]]
    return not any(s in hay for s in subs)


def check_starts_with(text: str, p: dict) -> bool:
    return text.lstrip().startswith(p["prefix"])


def check_ends_with(text: str, p: dict) -> bool:
    return text.rstrip().endswith(p["suffix"])


def check_json_valid(text: str, p: dict) -> bool:
    try:
        json.loads(text.strip())
        return True
    except (json.JSONDecodeError, ValueError):
        return False


def check_json_has_keys(text: str, p: dict) -> bool:
    try:
        obj = json.loads(text.strip())
    except (json.JSONDecodeError, ValueError):
        return False
    return isinstance(obj, dict) and all(k in obj for k in p["keys"])


def check_exact_line_count(text: str, p: dict) -> bool:
    lines = [ln for ln in text.strip().splitlines() if ln.strip()]
    return len(lines) == int(p["n"])


def check_max_sentences(text: str, p: dict) -> bool:
    sentences = [s for s in _SENTENCE_SPLIT.split(text.strip()) if s.strip()]
    return len(sentences) <= int(p["n"])


def check_regex_match(text: str, p: dict) -> bool:
    return re.search(p["pattern"], text) is not None


def check_no_markdown(text: str, p: dict) -> bool:
    return not re.search(r"[`*#_>]|\[.+?\]\(.+?\)", text)


def check_forbidden_words(text: str, p: dict) -> bool:
    low = text.lower()
    return not any(re.search(rf"\b{re.escape(w.lower())}\b", low) for w in p["words"])


CHECKERS: dict[str, Callable[[str, dict], bool]] = {
    "word_count_max": check_word_count_max,
    "word_count_min": check_word_count_min,
    "must_include_all": check_must_include_all,
    "must_not_include": check_must_not_include,
    "starts_with": check_starts_with,
    "ends_with": check_ends_with,
    "json_valid": check_json_valid,
    "json_has_keys": check_json_has_keys,
    "exact_line_count": check_exact_line_count,
    "max_sentences": check_max_sentences,
    "regex_match": check_regex_match,
    "no_markdown": check_no_markdown,
    "forbidden_words": check_forbidden_words,
}


# --- data model ----------------------------------------------------------------


@dataclass
class Constraint:
    type: str
    params: dict = field(default_factory=dict)

    def check(self, text: str) -> bool:
        if self.type not in CHECKERS:
            raise KeyError(f"unknown constraint type: {self.type}")
        return CHECKERS[self.type](text, self.params)

    def describe(self) -> str:
        if not self.params:
            return self.type
        return f"{self.type}({', '.join(f'{k}={v}' for k, v in self.params.items())})"


@dataclass
class EvalItem:
    id: str
    prompt: str
    constraints: list[Constraint]
    mock_response: str = ""

    @classmethod
    def from_dict(cls, d: dict) -> "EvalItem":
        cons = [Constraint(c["type"], {k: v for k, v in c.items() if k != "type"}) for c in d["constraints"]]
        return cls(id=d["id"], prompt=d["prompt"], constraints=cons, mock_response=d.get("mock_response", ""))


# --- scoring -------------------------------------------------------------------


def score_output(item: EvalItem, output: str) -> dict:
    checks = []
    for c in item.constraints:
        try:
            passed = c.check(output)
        except KeyError as exc:
            passed = False
            checks.append({"constraint": c.describe(), "passed": False, "error": str(exc)})
            continue
        checks.append({"constraint": c.describe(), "passed": passed})
    n = len(checks)
    n_pass = sum(1 for c in checks if c["passed"])
    return {
        "id": item.id,
        "constraint_satisfaction": n_pass / n if n else 1.0,
        "all_passed": n_pass == n,
        "n_constraints": n,
        "n_passed": n_pass,
        "checks": checks,
    }


def load_dataset(path: str) -> list[EvalItem]:
    items = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                items.append(EvalItem.from_dict(json.loads(line)))
    return items


def run_eval(items: list[EvalItem], generate: Callable[[str], str]) -> dict:
    per_item = [score_output(it, generate(it.prompt)) for it in items]
    n = len(per_item)
    return {
        "n_items": n,
        "mean_constraint_satisfaction": (
            sum(r["constraint_satisfaction"] for r in per_item) / n if n else 0.0
        ),
        "perfect_rate": (sum(1 for r in per_item if r["all_passed"]) / n if n else 0.0),
        "items": per_item,
    }
