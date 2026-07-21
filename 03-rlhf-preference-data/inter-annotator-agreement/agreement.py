"""Inter-annotator agreement metrics for labeling and preference data.

When several people label the same items, you need to know how much they actually
agree beyond chance. This module computes:

- observed (percent) agreement for a pair of annotators
- Cohen's kappa for two annotators
- Fleiss' kappa for any number of annotators (constant raters per item)

Input is a flat list of annotation rows: {"item": ..., "annotator": ..., "label": ...}.
"""
from __future__ import annotations

from collections import defaultdict
from itertools import combinations


def build_tables(rows: list[dict]) -> tuple[list, list, dict[str, dict]]:
    """Return (items, categories, per-annotator {item: label}) from annotation rows."""
    items, categories = [], []
    by_annotator: dict[str, dict] = defaultdict(dict)
    for r in rows:
        item, ann, label = r["item"], r["annotator"], r["label"]
        if item not in items:
            items.append(item)
        if label not in categories:
            categories.append(label)
        by_annotator[ann][item] = label
    return items, sorted(categories, key=str), dict(by_annotator)


def percent_agreement(labels_a: list, labels_b: list) -> float:
    if len(labels_a) != len(labels_b):
        raise ValueError("annotators must cover the same items")
    if not labels_a:
        return 1.0
    agree = sum(1 for a, b in zip(labels_a, labels_b, strict=True) if a == b)
    return agree / len(labels_a)


def cohens_kappa(labels_a: list, labels_b: list) -> float:
    """Cohen's kappa for two annotators over the same items."""
    if len(labels_a) != len(labels_b):
        raise ValueError("annotators must cover the same items")
    n = len(labels_a)
    if n == 0:
        return 1.0
    cats = set(labels_a) | set(labels_b)
    po = percent_agreement(labels_a, labels_b)
    pe = 0.0
    for c in cats:
        pa = labels_a.count(c) / n
        pb = labels_b.count(c) / n
        pe += pa * pb
    if pe == 1.0:  # both annotators used a single label for everything
        return 1.0 if po == 1.0 else 0.0
    return (po - pe) / (1 - pe)


def fleiss_kappa(matrix: list[list[int]]) -> float:
    """Fleiss' kappa from an items x categories count matrix.

    matrix[i][j] = number of annotators who put item i in category j.
    Every item must have the same total number of annotators.
    """
    if not matrix:
        raise ValueError("empty matrix")
    n_raters = sum(matrix[0])
    if n_raters < 2:
        raise ValueError("need at least 2 raters per item")
    if any(sum(row) != n_raters for row in matrix):
        raise ValueError("every item must have the same number of raters")

    n_items = len(matrix)
    total = n_items * n_raters
    p_j = [sum(matrix[i][j] for i in range(n_items)) / total for j in range(len(matrix[0]))]

    p_i = [
        (sum(c * c for c in row) - n_raters) / (n_raters * (n_raters - 1)) for row in matrix
    ]
    p_bar = sum(p_i) / n_items
    p_e = sum(p * p for p in p_j)
    if p_e == 1.0:
        return 1.0 if p_bar == 1.0 else 0.0
    return (p_bar - p_e) / (1 - p_e)


def _matrix_from_rows(rows: list[dict]) -> list[list[int]]:
    items, categories, by_annotator = build_tables(rows)
    cat_index = {c: j for j, c in enumerate(categories)}
    matrix = [[0] * len(categories) for _ in items]
    item_index = {it: i for i, it in enumerate(items)}
    for ann_labels in by_annotator.values():
        for item, label in ann_labels.items():
            matrix[item_index[item]][cat_index[label]] += 1
    return matrix


def analyze(rows: list[dict]) -> dict:
    """Full agreement report over a set of annotation rows."""
    items, categories, by_annotator = build_tables(rows)
    annotators = sorted(by_annotator, key=str)

    # pairwise metrics over items both annotators labeled
    pair_cohen, pair_pct = [], []
    for a, b in combinations(annotators, 2):
        shared = [it for it in items if it in by_annotator[a] and it in by_annotator[b]]
        la = [by_annotator[a][it] for it in shared]
        lb = [by_annotator[b][it] for it in shared]
        if shared:
            pair_cohen.append(cohens_kappa(la, lb))
            pair_pct.append(percent_agreement(la, lb))

    result = {
        "n_items": len(items),
        "n_annotators": len(annotators),
        "categories": categories,
        "mean_percent_agreement": round(sum(pair_pct) / len(pair_pct), 4) if pair_pct else None,
        "mean_pairwise_cohens_kappa": round(sum(pair_cohen) / len(pair_cohen), 4) if pair_cohen else None,
    }
    # Fleiss' kappa needs a constant number of raters per item
    counts = [sum(1 for ann in by_annotator.values() if it in ann) for it in items]
    if len(set(counts)) == 1 and counts and counts[0] >= 2:
        result["fleiss_kappa"] = round(fleiss_kappa(_matrix_from_rows(rows)), 4)
    else:
        result["fleiss_kappa"] = None
    return result
