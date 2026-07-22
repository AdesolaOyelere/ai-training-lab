"""Reference-based summary-quality scoring across three axes.

Judging summaries with another model is expensive and noisy. When each source ships
with its key points, three important axes can be scored deterministically:

- coverage      - what fraction of the source's key points the summary captures
- faithfulness  - whether the summary's content is supported by the source (a proxy for
                  hallucination: content words in the summary that never appear in the
                  source count against it)
- conciseness   - how much shorter the summary is than the source (with over-long
                  summaries penalized)

These are transparent proxies, not the last word on quality, but they catch the common
failure modes (missing points, invented facts, bloat) with no model in the loop.
"""
from __future__ import annotations

import re

_WORD = re.compile(r"[a-z0-9]+")
_STOP = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "for", "with", "is",
    "are", "was", "were", "be", "been", "it", "its", "this", "that", "these", "those",
    "as", "at", "by", "from", "into", "then", "than", "so", "if", "he", "she", "they",
    "we", "you", "i", "his", "her", "their", "our", "your", "them", "which", "who",
}


def _content_words(text: str) -> set[str]:
    return {w for w in _WORD.findall(text.lower()) if w not in _STOP and len(w) > 2}


def coverage(summary: str, key_points: list[str]) -> float:
    """Fraction of key points whose content words are (mostly) present in the summary."""
    if not key_points:
        return 1.0
    summ_words = _content_words(summary)
    hit = 0
    for kp in key_points:
        kp_words = _content_words(kp)
        if kp_words and len(kp_words & summ_words) / len(kp_words) >= 0.5:
            hit += 1
    return round(hit / len(key_points), 4)


def faithfulness(summary: str, source: str) -> float:
    """Fraction of the summary's content words that appear in the source."""
    summ_words = _content_words(summary)
    if not summ_words:
        return 1.0
    src_words = _content_words(source)
    supported = len(summ_words & src_words)
    return round(supported / len(summ_words), 4)


def conciseness(summary: str, source: str) -> float:
    """1.0 when the summary is much shorter than the source; drops toward 0 as it
    approaches or exceeds the source length."""
    s_len = len(_WORD.findall(summary))
    src_len = len(_WORD.findall(source))
    if src_len == 0:
        return 1.0
    ratio = s_len / src_len
    if ratio >= 1.0:
        return 0.0
    return round(1.0 - ratio, 4)


def score_summary(item: dict) -> dict:
    cov = coverage(item["summary"], item["key_points"])
    faith = faithfulness(item["summary"], item["source"])
    conc = conciseness(item["summary"], item["source"])
    overall = round(0.4 * cov + 0.4 * faith + 0.2 * conc, 4)
    return {
        "id": item.get("id"),
        "coverage": cov,
        "faithfulness": faith,
        "conciseness": conc,
        "overall": overall,
    }


def evaluate(items: list[dict]) -> dict:
    per_item = [score_summary(it) for it in items]
    n = len(per_item)

    def avg(key: str) -> float:
        return round(sum(r[key] for r in per_item) / n, 4) if n else 0.0

    return {
        "n": n,
        "mean_coverage": avg("coverage"),
        "mean_faithfulness": avg("faithfulness"),
        "mean_conciseness": avg("conciseness"),
        "mean_overall": avg("overall"),
        "per_item": per_item,
    }
