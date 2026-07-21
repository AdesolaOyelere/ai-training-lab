# Chat Format Converter

> Normalize supervised fine-tuning data between the three formats every dataset
> seems to pick differently — ShareGPT, OpenAI `messages`, and simple
> `prompt`/`response` — with validation and single-turn safety checks.

**Category:** `07-finetuning` · **Skills:** SFT data engineering, CLI, Python (standard library)

## Problem

Before you can fine-tune on, or mix, several datasets, they all have to be in one
schema. In practice sources arrive as ShareGPT (`from`/`value`), OpenAI chat
(`role`/`content`), or flat `prompt`/`response` pairs, and hand-converting them is
where silent data bugs creep in — a dropped system prompt, a mislabeled role, or a
multi-turn conversation flattened into a single answer.

## Approach

Everything is normalized to the OpenAI `messages` representation internally, then
emitted in the target format. That keeps role mapping in exactly one place
(`human↔user`, `gpt↔assistant`, `system↔system`) and means each new format is just a
`to_messages` and a `from_messages` function.

Safety checks that prevent silent corruption:

- roles are validated; unknown senders raise instead of passing through,
- converting to `prompt_response` **refuses** multi-turn conversations rather than
  quietly dropping turns,
- file conversion reports the **line number** of the first bad record.

## How to run

```bash
python -m pytest

# ShareGPT -> OpenAI messages
python convert.py sample_data/sharegpt.jsonl --from sharegpt --to messages -o out.jsonl

# messages -> prompt/response (single-turn only)
python convert.py out.jsonl --from messages --to prompt_response
```

## Sample output

`sample_data/sharegpt.jsonl` converted to `messages` (`results/messages.jsonl`):

```json
{"messages": [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "What is 2 + 2?"}, {"role": "assistant", "content": "2 + 2 = 4."}]}
```

The second sample record is multi-turn, so converting it to `prompt_response` raises
a clear error pointing at the offending line — by design.

## What this demonstrates

- Practical **data-engineering** for training pipelines: schema normalization done
  once, cleanly.
- Defensive conversion that **fails loudly** on data it cannot represent instead of
  corrupting it silently.
- A tidy CLI plus a fully tested core, no third-party runtime dependencies.
