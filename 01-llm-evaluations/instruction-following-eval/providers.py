"""Model providers behind a single `generate(prompt) -> str` interface.

The mock provider replays committed responses so the eval is fully reproducible
offline (and in CI). The Anthropic provider calls a live model when a key is set.
Swapping providers never touches the eval logic.
"""
from __future__ import annotations

import os
from typing import Callable

Provider = Callable[[str], str]


def mock_provider(prompt_to_response: dict[str, str]) -> Provider:
    """Return canned responses; falls back to an empty string for unknown prompts."""

    def generate(prompt: str) -> str:
        return prompt_to_response.get(prompt, "")

    return generate


def anthropic_provider(model: str = "claude-sonnet-5", max_tokens: int = 1024) -> Provider:
    """Live Anthropic provider. Requires ANTHROPIC_API_KEY and the `anthropic` package."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set")

    import anthropic  # imported lazily so the mock path needs no dependency

    client = anthropic.Anthropic(api_key=api_key)

    def generate(prompt: str) -> str:
        msg = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in msg.content if block.type == "text")

    return generate
