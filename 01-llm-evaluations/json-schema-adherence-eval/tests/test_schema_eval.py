"""Tests for the schema-adherence eval: each failure mode is detected, extra fields
are allowed, bool is not a number, and the aggregate over the committed dataset (with
one of each failure type) is pinned."""
import json
from pathlib import Path

from schema_eval import check, evaluate

HERE = Path(__file__).resolve().parent.parent

SCHEMA = {
    "fields": {
        "sentiment": {"type": "string", "required": True, "enum": ["positive", "negative", "neutral"]},
        "confidence": {"type": "number", "required": True},
    }
}


def errs(output):
    return check(output, SCHEMA)["errors"]


def test_conformant_output():
    assert check('{"sentiment": "positive", "confidence": 0.9}', SCHEMA)["conformant"]


def test_each_failure_mode():
    assert errs("not json at all") == ["invalid_json"]
    assert errs("[1, 2, 3]") == ["not_an_object"]
    assert errs('{"confidence": 0.5}') == ["missing:sentiment"]
    assert errs('{"sentiment": "positive", "confidence": "high"}') == ["type:confidence"]
    assert errs('{"sentiment": "mixed", "confidence": 0.5}') == ["enum:sentiment"]


def test_extra_fields_allowed():
    out = '{"sentiment": "negative", "confidence": 0.9, "note": "extra"}'
    assert check(out, SCHEMA)["conformant"]


def test_bool_is_not_a_number():
    assert errs('{"sentiment": "positive", "confidence": true}') == ["type:confidence"]


def test_aggregate_pins_committed_results():
    outputs = [json.loads(x)["output"] for x in (HERE / "dataset.jsonl").read_text().splitlines() if x.strip()]
    schema = json.loads((HERE / "schema.json").read_text(encoding="utf-8"))
    m = evaluate(outputs, schema)
    assert m["n"] == 8
    # conformant: s1, s2, s4, s8 ; fail: s3 (json prose), s5 (type), s6 (missing), s7 (enum)
    assert m["n_conformant"] == 4
    assert m["conformance_rate"] == 0.5
    assert m["failure_reasons"] == {"enum": 1, "invalid_json": 1, "missing": 1, "type": 1}
    committed = json.loads((HERE / "results" / "results.json").read_text(encoding="utf-8"))
    assert committed == m
