"""Tests for PII detection: each type is found, the Luhn check rejects invalid card
numbers, invalid IPs are rejected, redaction masks spans, and the labeled-set metrics
are strong (perfect on this set)."""
import json
from pathlib import Path

from pii import evaluate, find_pii, redact

HERE = Path(__file__).resolve().parent.parent


def types_found(text: str) -> set[str]:
    return {s["type"] for s in find_pii(text)}


def test_each_type_detected():
    assert "email" in types_found("reach me at a.b@example.com")
    assert "phone" in types_found("call (555) 123-4567 now")
    assert "ssn" in types_found("ssn 123-45-6789")
    assert "credit_card" in types_found("card 4111 1111 1111 1111")
    assert "ipv4" in types_found("from 192.168.1.100 tonight")


def test_luhn_rejects_invalid_card():
    # a 16-digit number that fails the Luhn checksum should not be flagged as a card
    assert "credit_card" not in types_found("number 1234 5678 9012 3456")
    assert "credit_card" in types_found("number 4111 1111 1111 1111")


def test_invalid_ip_rejected():
    assert "ipv4" not in types_found("build 999.999.999.999 failed")
    assert "ipv4" in types_found("host 10.0.0.1 responded")


def test_clean_text_has_no_pii():
    assert find_pii("The meeting is at 3pm in room 204.") == []


def test_redaction_masks_all_spans():
    red = redact("email a.b@example.com and call (555) 123-4567")
    assert "a.b@example.com" not in red
    assert "555" not in red
    assert red.count("[REDACTED]") == 2


def test_evaluation_on_labeled_set():
    rows = [json.loads(x) for x in (HERE / "dataset.jsonl").read_text().splitlines() if x.strip()]
    m = evaluate(rows)
    assert m["n"] == 11
    # the patterns cleanly separate the labeled benign/PII rows here
    assert m["confusion"] == {"tp": 6, "fp": 0, "tn": 5, "fn": 0}
    assert m["precision"] == 1.0 and m["recall"] == 1.0
