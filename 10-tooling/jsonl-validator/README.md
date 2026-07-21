# JSONL Validator

> A dependency-free command-line tool that lints the JSONL files used for SFT,
> evals, and preference data — catching broken JSON, missing or mistyped fields,
> and duplicate keys before they poison a training run.

**Category:** `10-tooling` · **Skills:** CLI design, data validation, Python (standard library only)

## Problem

Training and eval datasets live in JSONL, and a single malformed line — a trailing
comma, an empty `response`, a duplicated `id`, a `score` that is a string — can
silently corrupt a run or crash a loader deep in a pipeline. You want to catch that
at the door, in CI or a pre-commit hook.

## Approach

`validate_lines()` walks the file once and collects a list of `Issue`s, each tagged
with a line number and a machine-readable kind:

- `invalid_json`, `not_an_object`
- `missing_field`, `empty_field` (for `--require`)
- `wrong_type`, `unknown_type` (for `--types`, with `bool` correctly *not* counting
  as a number)
- `duplicate_key` (for `--unique`, pointing back to the first occurrence)
- `blank_line` (optional)

The CLI wraps that with argument parsing and standard exit codes: `0` clean, `1`
issues found, `2` file unreadable.

## How to run

```bash
python -m pytest

# validate a dataset
python jsonl_validator.py sample_data/good.jsonl --require id,prompt,response --unique id
# -> OK: 3 records valid in sample_data/good.jsonl

python jsonl_validator.py sample_data/bad.jsonl --require id,prompt,response --types score:number --unique id
# -> line 2: empty_field: response
#    line 3: wrong_type: score is str, want number
#    line 3: duplicate_key: id='ex2' first seen on line 2
#    line 4: missing_field: response
#    line 5: invalid_json: Expecting property name enclosed in double quotes
#    line 6: not_an_object: got list
#    FAIL: 6 issue(s) across 6 records in sample_data/bad.jsonl
```

## What this demonstrates

- A clean, well-argued **CLI** with sensible exit codes that slots into automation.
- Careful data-validation logic, including the easy-to-miss detail that `True` is an
  `int` in Python and must not pass a numeric type check.
- Zero third-party dependencies and a full test suite covering each issue kind.
