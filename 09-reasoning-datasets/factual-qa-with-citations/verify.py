"""Verify citation-grounded question answering.

A trustworthy QA item cites the source sentences that support its answer. This verifier
checks two things per item: (1) every citation points to a real source sentence, and
(2) the answer is actually supported by the cited sentences (its content words appear in
what it cited, not elsewhere or nowhere). That distinguishes a genuinely grounded answer
from one that cites unrelated sentences or makes uncited claims — the core check behind
attribution and RAG faithfulness.
"""
from __future__ import annotations

import re

_WORD = re.compile(r"[a-z0-9]+")
_STOP = {
    "the", "a", "an", "and", "or", "of", "to", "in", "on", "for", "with", "is", "are",
    "was", "were", "be", "it", "its", "this", "that", "as", "at", "by", "from", "which",
    "who", "what", "when", "where", "how", "why", "did", "do", "does",
}


def _content(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if w not in _STOP and len(w) > 2}


def verify_item(item: dict, support_threshold: float = 0.6) -> dict:
    """Check one QA item.

    item = {question, source: [{id, text}], answer, citations: [id]}.
    """
    by_id = {s["id"]: s["text"] for s in item["source"]}
    citations = item["citations"]

    invalid = [c for c in citations if c not in by_id]
    valid_citations = [c for c in citations if c in by_id]

    cited_text = " ".join(by_id[c] for c in valid_citations)
    ans_words = _content(item["answer"])
    cited_words = _content(cited_text)

    if not ans_words:
        support = 1.0
    else:
        support = len(ans_words & cited_words) / len(ans_words)

    has_citation = len(valid_citations) > 0
    grounded = has_citation and support >= support_threshold and not invalid
    return {
        "id": item.get("id"),
        "has_valid_citation": has_citation,
        "invalid_citations": invalid,
        "support": round(support, 4),
        "grounded": grounded,
    }


def evaluate(items: list[dict], support_threshold: float = 0.6) -> dict:
    rows = [verify_item(it, support_threshold) for it in items]
    n = len(rows)
    return {
        "n": n,
        "grounded_rate": round(sum(1 for r in rows if r["grounded"]) / n, 4) if n else 0.0,
        "mean_support": round(sum(r["support"] for r in rows) / n, 4) if n else 0.0,
        "n_with_invalid_citations": sum(1 for r in rows if r["invalid_citations"]),
        "per_item": rows,
    }
