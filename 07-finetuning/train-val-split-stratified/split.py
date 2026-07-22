"""Stratified, leakage-safe train/val/test splitting.

Two mistakes quietly ruin a fine-tuning eval: an unstratified split that skews the
label balance between train and test, and leakage, where the same (or a duplicate)
example lands in both train and test so the model is scored on data it trained on. This
splitter avoids both — it groups duplicate texts so a group never spans splits, and it
allocates each label's groups across splits to preserve class proportions. It is
deterministic given a seed.
"""
from __future__ import annotations

import hashlib
import re
from collections import defaultdict

_WS = re.compile(r"\s+")


def _norm(text: str) -> str:
    return _WS.sub(" ", text.strip().lower())


def _group_key(text: str) -> str:
    return hashlib.md5(_norm(text).encode()).hexdigest()  # noqa: S324 - not security-sensitive


def _seeded_order(items: list, seed: int) -> list:
    """Deterministic shuffle: order by a hash of (seed, key)."""
    return sorted(items, key=lambda k: hashlib.md5(f"{seed}:{k}".encode()).hexdigest())  # noqa: S324


def split(rows: list[dict], ratios=(0.6, 0.2, 0.2), seed: int = 0) -> dict:
    """Split rows ({text, label}) into train/val/test.

    Duplicate texts share a group and stay together; within each label, groups are
    allocated to splits to match the target ratios as closely as integer counts allow.
    """
    assert abs(sum(ratios) - 1.0) < 1e-9, "ratios must sum to 1"

    # group duplicate texts (leakage units), remembering each group's label
    groups: dict[str, dict] = {}
    for i, row in enumerate(rows):
        key = _group_key(row["text"])
        g = groups.setdefault(key, {"indices": [], "label": row["label"]})
        g["indices"].append(i)

    # per label, order groups deterministically and allocate to splits by ratio
    by_label: dict[str, list[str]] = defaultdict(list)
    for key, g in groups.items():
        by_label[g["label"]].append(key)

    assignment: dict[str, str] = {}   # group key -> split name
    names = ["train", "val", "test"]
    for keys in by_label.values():
        ordered = _seeded_order(keys, seed)
        n = len(ordered)
        n_train = round(n * ratios[0])
        n_val = round(n * ratios[1])
        for idx, key in enumerate(ordered):
            if idx < n_train:
                assignment[key] = "train"
            elif idx < n_train + n_val:
                assignment[key] = "val"
            else:
                assignment[key] = "test"

    splits: dict[str, list[dict]] = {n: [] for n in names}
    for key, g in groups.items():
        target = assignment[key]
        for i in g["indices"]:
            splits[target].append(rows[i])
    return splits


def _label_props(rows: list[dict]) -> dict[str, float]:
    counts: dict[str, int] = defaultdict(int)
    for r in rows:
        counts[r["label"]] += 1
    total = len(rows)
    return {k: round(v / total, 4) for k, v in sorted(counts.items())} if total else {}


def check_no_leakage(splits: dict) -> bool:
    """True if no normalized text appears in more than one split."""
    seen: dict[str, str] = {}
    for name, rows in splits.items():
        for r in rows:
            key = _group_key(r["text"])
            if key in seen and seen[key] != name:
                return False
            seen[key] = name
    return True


def report(rows: list[dict], splits: dict) -> dict:
    return {
        "total": len(rows),
        "sizes": {name: len(rs) for name, rs in splits.items()},
        "overall_label_props": _label_props(rows),
        "split_label_props": {name: _label_props(rs) for name, rs in splits.items()},
        "no_leakage": check_no_leakage(splits),
    }
