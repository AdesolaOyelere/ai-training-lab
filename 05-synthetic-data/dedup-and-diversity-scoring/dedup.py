"""Near-duplicate removal and diversity scoring for a text dataset.

Synthetic datasets drift toward repetition: the same instruction reworded, the same
answer template over and over. Two things keep a set healthy — removing near
duplicates and measuring how diverse what's left actually is. Both are done here with
transparent character-n-gram Jaccard similarity (no embeddings, no dependencies), so
the whole thing runs anywhere and is fully testable.
"""
from __future__ import annotations

import re

_WORD = re.compile(r"\w+")


def normalize(text: str) -> str:
    return " ".join(_WORD.findall(text.lower()))


def shingles(text: str, k: int = 4) -> set[str]:
    """Character k-gram shingles of the normalized text."""
    s = normalize(text)
    if len(s) < k:
        return {s} if s else set()
    return {s[i : i + k] for i in range(len(s) - k + 1)}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union


def similarity(x: str, y: str, k: int = 4) -> float:
    return jaccard(shingles(x, k), shingles(y, k))


def dedupe(texts: list[str], threshold: float = 0.6, k: int = 4) -> dict:
    """Greedy near-dup removal: keep an item unless it is >= threshold similar to one
    already kept. Returns kept indices, removed pairs, and the kept texts."""
    kept_idx: list[int] = []
    kept_shingles: list[set[str]] = []
    removed: list[dict] = []
    for i, t in enumerate(texts):
        sh = shingles(t, k)
        dup_of = None
        for j, ks in zip(kept_idx, kept_shingles, strict=True):
            if jaccard(sh, ks) >= threshold:
                dup_of = j
                break
        if dup_of is None:
            kept_idx.append(i)
            kept_shingles.append(sh)
        else:
            removed.append({"index": i, "duplicate_of": dup_of})
    return {
        "kept_indices": kept_idx,
        "removed": removed,
        "kept_texts": [texts[i] for i in kept_idx],
        "n_in": len(texts),
        "n_kept": len(kept_idx),
        "n_removed": len(removed),
    }


def diversity_score(texts: list[str], k: int = 4) -> float:
    """Mean pairwise dissimilarity (1 - Jaccard) over the set; 1.0 = all distinct."""
    n = len(texts)
    if n < 2:
        return 1.0
    shs = [shingles(t, k) for t in texts]
    total, pairs = 0.0, 0
    for i in range(n):
        for j in range(i + 1, n):
            total += 1.0 - jaccard(shs[i], shs[j])
            pairs += 1
    return round(total / pairs, 4)


def analyze(texts: list[str], threshold: float = 0.6, k: int = 4) -> dict:
    result = dedupe(texts, threshold, k)
    return {
        **result,
        "diversity_before": diversity_score(texts, k),
        "diversity_after": diversity_score(result["kept_texts"], k),
    }
