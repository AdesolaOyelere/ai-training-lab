"""Clean and format a raw dataset into a ready-to-train SFT set.

Raw supervised-fine-tuning data is messy: blank fields, whitespace, exact and
near-exact duplicates, truncated answers, prompts that are too long, and stray
placeholder rows. This pipeline applies a documented sequence of filters, emits the
survivors in OpenAI `messages` format, and returns a report explaining exactly how
many rows each stage dropped — the kind of provenance you attach to a dataset release.
"""
from __future__ import annotations

import re

_WS = re.compile(r"\s+")
_PLACEHOLDER = re.compile(r"^\s*(TODO|TBD|N/?A|xxx+|lorem ipsum)\s*$", re.IGNORECASE)


def normalize_ws(text: str) -> str:
    return _WS.sub(" ", text).strip()


def is_placeholder(text: str) -> bool:
    return bool(_PLACEHOLDER.match(text.strip()))


def prepare(
    rows: list[dict],
    min_prompt_chars: int = 3,
    min_response_chars: int = 1,
    max_prompt_chars: int = 2000,
    max_response_chars: int = 4000,
) -> dict:
    """Run the cleaning pipeline. Each row should have 'prompt' and 'response'.

    Returns {"records": [...messages...], "report": {...stage counts...}}.
    """
    stages = {
        "input": len(rows),
        "dropped_missing_field": 0,
        "dropped_empty": 0,
        "dropped_placeholder": 0,
        "dropped_too_short": 0,
        "dropped_too_long": 0,
        "dropped_duplicate": 0,
    }
    seen: set[tuple[str, str]] = set()
    records: list[dict] = []

    for row in rows:
        if "prompt" not in row or "response" not in row:
            stages["dropped_missing_field"] += 1
            continue
        prompt = normalize_ws(str(row["prompt"]))
        response = normalize_ws(str(row["response"]))

        if not prompt or not response:
            stages["dropped_empty"] += 1
            continue
        if is_placeholder(prompt) or is_placeholder(response):
            stages["dropped_placeholder"] += 1
            continue
        if len(prompt) < min_prompt_chars or len(response) < min_response_chars:
            stages["dropped_too_short"] += 1
            continue
        if len(prompt) > max_prompt_chars or len(response) > max_response_chars:
            stages["dropped_too_long"] += 1
            continue

        key = (prompt.lower(), response.lower())
        if key in seen:
            stages["dropped_duplicate"] += 1
            continue
        seen.add(key)

        record = {"messages": [
            {"role": "user", "content": prompt},
            {"role": "assistant", "content": response},
        ]}
        if row.get("system"):
            record["messages"].insert(0, {"role": "system", "content": normalize_ws(str(row["system"]))})
        records.append(record)

    stages["kept"] = len(records)
    stages["keep_rate"] = round(len(records) / len(rows), 4) if rows else 0.0
    return {"records": records, "report": stages}
