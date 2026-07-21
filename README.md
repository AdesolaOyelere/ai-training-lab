# AI Training Lab

A working portfolio of AI training, evaluation, and data engineering — plus the Python
tooling that supports it. Everything here is original, open source, and reproducible.

I build and evaluate the data that trains language models: evals and benchmarks,
preference and RLHF datasets, synthetic data pipelines, agentic tasks, annotation
guidelines, and the CLIs and small apps that keep that work clean.

**Author:** Adesola Oyelere
**License:** MIT · **Language:** Python 3.11+

---

## What this shows

| Skill area | Where to look |
|---|---|
| LLM evaluation & benchmarking | [`01-llm-evaluations/`](01-llm-evaluations/) |
| Prompt engineering | [`02-prompt-engineering/`](02-prompt-engineering/) |
| RLHF & preference data | [`03-rlhf-preference-data/`](03-rlhf-preference-data/) |
| Red-teaming & AI safety | [`04-red-teaming-safety/`](04-red-teaming-safety/) |
| Synthetic data generation | [`05-synthetic-data/`](05-synthetic-data/) |
| Agentic & tool-use task design | [`06-agentic-tasks/`](06-agentic-tasks/) |
| Fine-tuning & training | [`07-finetuning/`](07-finetuning/) |
| Annotation guidelines & rubrics | [`08-annotation-guidelines/`](08-annotation-guidelines/) |
| Reasoning & domain datasets | [`09-reasoning-datasets/`](09-reasoning-datasets/) |
| Tooling, CLIs & mini-apps | [`10-tooling/`](10-tooling/) |

The full roadmap of projects lives in [`PROJECTS.md`](PROJECTS.md).

---

## How this repo is built

Every project is self-contained and follows the same shape:

```
<category>/<project>/
  README.md      problem -> approach -> how to run -> sample output -> skill shown
  meta.json      machine-readable metadata (feeds the index)
  <code>         runnable Python, small and focused
  tests/         unit tests on the deterministic core
  results/       committed sample output so it is viewable without running anything
```

Design rules that keep 100 projects consistent:

- **Reproducible offline.** Any project that calls a model hides it behind a provider
  interface with a deterministic mock, so tests and CI never need an API key. Real
  sample outputs are committed.
- **The core is pure Python and tested.** Scoring, parsing, filtering, and metrics are
  unit-tested; the model call is the thin, swappable part.
- **One system.** A shared README template and a metadata-driven index generator keep
  every folder looking and reading the same way.

---

## Quick start

```bash
git clone https://github.com/AdesolaOyelere/ai-training-lab
cd ai-training-lab

# dev tooling (ruff + pytest) via uv
uv sync

# run any project's tests
cd 01-llm-evaluations/instruction-following-eval
python -m pytest
```

To use live models, set `ANTHROPIC_API_KEY`. Without it, everything still runs on the
committed mock provider and sample data.

---

## Rebuilding the index

Project tables in this README and `PROJECTS.md` are generated from each project's
`meta.json`:

```bash
python scripts/gen_index.py
```

<!-- INDEX:SUMMARY:START -->
**12** projects tracked · ✅ 12 done · 🔨 0 in progress · ⬜ 0 planned
<!-- INDEX:SUMMARY:END -->
