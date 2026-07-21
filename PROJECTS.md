# Projects

The full roadmap. Target is ~100 focused, self-contained projects across ten skill
areas. Quality over count — nothing is padding.

**Legend:** ✅ done · 🔨 in progress · ⬜ planned

The table below is generated from each project's `meta.json` (run
`python scripts/gen_index.py`). The checklist under it is the hand-maintained backlog.

<!-- INDEX:TABLE:START -->
| Project | Category | Status | Summary |
|---|---|---|---|
| [Instruction-Following Eval](01-llm-evaluations/instruction-following-eval/) | `01-llm-evaluations` | ✅ | Grades model outputs against programmatically checkable constraints (word counts, required keywords, valid JSON, structure) with no subjective judging. |
| [LLM-as-Judge Harness](01-llm-evaluations/llm-as-judge-harness/) | `01-llm-evaluations` | ✅ | Pairwise LLM-as-judge with order-swap debiasing: judges each pair in both orders, counts a win only on agreement, and reports a measured position-bias rate. |
| [Prompt Linter](02-prompt-engineering/prompt-linter/) | `02-prompt-engineering` | ✅ | Flags prompt anti-patterns (no output format, undelimited input, conflicting length, vague quantifiers, structure without an example) and scores a prompt 0-100 — best practices as code. |
| [Inter-Annotator Agreement](03-rlhf-preference-data/inter-annotator-agreement/) | `03-rlhf-preference-data` | ✅ | Computes percent agreement, Cohen's kappa, and Fleiss' kappa from annotation rows to measure how much labelers agree beyond chance — validated against textbook values. |
| [PII Leak Detector](04-red-teaming-safety/pii-leak-detector/) | `04-red-teaming-safety` | ✅ | Finds and redacts PII (emails, phones, SSNs, credit cards with a Luhn check, IPv4) in text, scored with precision/recall on a labeled set — a defensive scrubbing utility. |
| [Prompt-Injection Detector](04-red-teaming-safety/prompt-injection-detector/) | `04-red-teaming-safety` | ✅ | A defensive rule-based detector that flags injection attempts in untrusted content (override, exfiltration, role spoofing, destructive commands), scored with precision/recall/F1 against a labeled set. |
| [Dedup & Diversity Scoring](05-synthetic-data/dedup-and-diversity-scoring/) | `05-synthetic-data` | ✅ | Removes near-duplicate dataset entries with character n-gram Jaccard similarity and scores diversity before and after — no embeddings, fully deterministic. |
| [Reasoning-Trace Generator](05-synthetic-data/reasoning-trace-generator/) | `05-synthetic-data` | ✅ | Generates step-by-step reasoning traces and keeps only those an independent reference verifies, with dedup and length filtering — rejection sampling for a clean training set. |
| [Tool-Calling Eval Harness](06-agentic-tasks/tool-calling-eval-harness/) | `06-agentic-tasks` | ✅ | Scores an agent's tool calls on schema validity, tool selection, and argument correctness against a tool catalog and expected calls, rolled up into tracked rates. |
| [Chat Format Converter](07-finetuning/chat-format-converter/) | `07-finetuning` | ✅ | Converts SFT chat data between ShareGPT, OpenAI messages, and prompt/response formats via a single normalized representation, with validation and clear errors. |
| [Summary Quality Rubric](08-annotation-guidelines/summary-quality-rubric/) | `08-annotation-guidelines` | ✅ | An annotation handbook for rating summary quality (coverage, faithfulness, conciseness, fluency) with a faithfulness gate, plus executable rubric code that reproduces every gold calibration label. |
| [Math Word Problems (Graded)](09-reasoning-datasets/math-word-problems-graded/) | `09-reasoning-datasets` | ✅ | A math word-problem dataset with a robust final-answer checker that normalizes numbers, treats equivalent fractions as equal, and matches text labels — then grades a whole set by type. |
| [JSONL Validator](10-tooling/jsonl-validator/) | `10-tooling` | ✅ | A dependency-free CLI that lints JSONL datasets — valid JSON, required and typed fields, unique keys — and exits non-zero on problems so it fits CI. |
| [Token & Cost Counter](10-tooling/token-counter/) | `10-tooling` | ✅ | A CLI that estimates token counts with a transparent heuristic and computes exact API cost from a per-model price table, for budgeting text or sizing a JSONL dataset. |
<!-- INDEX:TABLE:END -->

---

## Backlog

### 01 · LLM Evaluations & Benchmarks
- ✅ `instruction-following-eval` — rubric-based scoring of multi-constraint prompts
- ⬜ `hallucination-faithfulness-eval` — faithfulness scoring against source context
- ✅ `llm-as-judge-harness` — judge with position/verbosity bias controls
- ⬜ `json-schema-adherence-eval` — structured-output conformance rate
- ⬜ `summarization-quality-eval` — coverage / faithfulness / conciseness
- ⬜ `rag-answer-grounding-eval` — is the answer supported by retrieved chunks
- ⬜ `multi-turn-consistency-eval` — contradiction detection across a conversation
- ⬜ `refusal-calibration-eval` — refuse the unsafe, answer the benign
- ⬜ `code-generation-unit-test-eval` — pass@k against hidden unit tests
- ⬜ `math-word-problem-eval` — exact-match + reasoning-step scoring
- ⬜ `long-context-retrieval-eval` — needle-in-a-haystack at varying depths
- ⬜ `pairwise-model-comparison-arena` — Elo from pairwise judgments

### 02 · Prompt Engineering
- ✅ `prompt-linter` — flag prompt anti-patterns and score prompt quality
- ⬜ `few-shot-vs-zeroshot-ablation` — measured effect of exemplars
- ⬜ `chain-of-thought-study` — CoT vs direct on reasoning tasks
- ⬜ `system-prompt-design-lab` — persona/constraint system-prompt studies
- ⬜ `structured-output-reliability` — JSON-mode reliability under stress
- ⬜ `self-consistency-voting` — majority vote over sampled chains
- ⬜ `prompt-compression-study` — token savings vs quality loss
- ⬜ `role-persona-prompting` — persona effects on tone and accuracy
- ⬜ `delimiter-and-formatting-study` — how structure changes obedience
- ⬜ `rubric-in-prompt-grading` — embedding a rubric into a grader prompt
- ⬜ `negative-instruction-following` — "do not" constraints
- ⬜ `prompt-versioning-registry` — track and diff prompt versions

### 03 · RLHF & Preference Data
- ⬜ `preference-dataset-builder` — build a chosen/rejected set with a guide
- ⬜ `pairwise-ranking-rubric` — rubric + worked calibration examples
- ✅ `inter-annotator-agreement` — Cohen's / Fleiss' kappa report
- ⬜ `reward-model-scoring-notebook` — score responses, inspect margins
- ⬜ `response-quality-taxonomy` — a taxonomy of failure modes
- ⬜ `helpful-harmless-honest-rubric` — HHH rubric with edge cases
- ⬜ `preference-data-format-converter` — to/from common RLHF formats
- ⬜ `tie-and-both-bad-handling` — protocol for hard preference cases
- ⬜ `length-bias-audit` — detect length bias in preferences
- ⬜ `preference-noise-simulation` — how label noise moves a reward signal

### 04 · Red-teaming & AI Safety
- ⬜ `refusal-over-refusal-eval` — balance safety and helpfulness
- ✅ `prompt-injection-detector` — flag injections in untrusted content
- ⬜ `adversarial-prompt-taxonomy` — categorize adversarial inputs
- ⬜ `jailbreak-pattern-catalog` — defensive analysis of known patterns
- ⬜ `safety-rubric-annotation-guide` — how to label safety violations
- ✅ `pii-leak-detector` — flag PII in model outputs
- ⬜ `tool-use-guardrail-tests` — guardrails on dangerous tool calls
- ⬜ `harmful-request-classifier` — classify request risk levels
- ⬜ `sycophancy-eval` — does the model cave to pushback
- ⬜ `content-policy-boundary-cases` — the hard middle of a policy

### 05 · Synthetic Data Generation
- ✅ `reasoning-trace-generator` — generate + quality-filter reasoning traces
- ⬜ `instruction-response-pipeline` — instruction -> response with filtering
- ⬜ `self-critique-refinement-loop` — draft -> critique -> revise
- ✅ `dedup-and-diversity-scoring` — near-dup removal + diversity metric
- ⬜ `persona-driven-dialogue-gen` — multi-persona dialogues
- ⬜ `math-problem-generator` — templated problems with checked answers
- ⬜ `code-qa-pair-generator` — code + question + verified answer
- ⬜ `data-augmentation-paraphrase` — controlled paraphrase augmentation
- ⬜ `quality-filter-pipeline` — heuristic + model-scored filtering
- ⬜ `seed-to-dataset-expander` — grow a seed set with diversity control

### 06 · Agentic & Tool-use Tasks
- ✅ `tool-calling-eval-harness` — score tool-call correctness
- ⬜ `multi-step-planning-tasks` — tasks needing a plan, with checkers
- ⬜ `function-schema-validator` — validate tool-call args against schema
- ⬜ `react-agent-mini` — a small ReAct loop over mock tools
- ⬜ `web-search-agent-eval` — evaluate a (mocked) search agent
- ⬜ `calculator-tool-agent` — arithmetic agent with a tool
- ⬜ `file-ops-sandbox-tasks` — sandboxed file-operation tasks
- ⬜ `agent-trajectory-scorer` — score an agent trajectory against a rubric
- ⬜ `retry-and-recovery-eval` — does the agent recover from errors
- ⬜ `tool-selection-accuracy` — picks the right tool for the job

### 07 · Fine-tuning & Training
- ⬜ `sft-data-prep` — clean + format an SFT dataset
- ⬜ `tokenization-cost-analysis` — token/cost accounting across datasets
- ⬜ `eval-before-after-harness` — compare a model pre/post tuning
- ✅ `chat-format-converter` — ShareGPT / messages / JSONL converters
- ⬜ `lora-config-explainer` — annotated LoRA config walkthrough
- ⬜ `dataset-decontamination` — remove eval leakage from train data
- ⬜ `train-val-split-stratified` — stratified, leakage-safe splits
- ⬜ `loss-curve-reader` — parse and summarize training logs

### 08 · Annotation Guidelines & Rubrics
- ✅ `summary-quality-rubric` — full handbook + executable rubric for summary labeling
- ⬜ `edge-case-catalog` — the tricky cases every annotator hits
- ⬜ `calibration-example-set` — gold examples with reasoning
- ⬜ `qa-spotcheck-protocol` — quality-control sampling protocol
- ⬜ `labeling-schema-design` — design a label schema from scratch
- ⬜ `disagreement-resolution-guide` — adjudicating annotator disputes
- ⬜ `rubric-to-checklist-converter` — turn a rubric into a checklist tool
- ⬜ `annotation-throughput-tracker` — track speed vs quality

### 09 · Reasoning & Domain Datasets
- ✅ `math-word-problems-graded` — problems with step-checked solutions
- ⬜ `logic-puzzles-with-checkers` — puzzles + programmatic verifiers
- ⬜ `code-review-qa-pairs` — review question/answer pairs
- ⬜ `factual-qa-with-citations` — answers with source citations
- ⬜ `unit-conversion-dataset` — conversions with a checker
- ⬜ `sql-query-tasks-graded` — NL -> SQL with result-set checking
- ⬜ `reading-comprehension-set` — passage + Q + graded answer
- ⬜ `commonsense-reasoning-set` — commonsense items with rationales
- ⬜ `multistep-arithmetic-graded` — multi-step arithmetic with checks
- ⬜ `constraint-satisfaction-puzzles` — CSPs with solvers as checkers

### 10 · Tooling, CLIs & Mini-Apps
- ✅ `jsonl-validator` — CLI that lints and validates JSONL datasets
- ⬜ `dataset-deduper` — CLI near-duplicate remover
- ✅ `token-counter` — CLI token/cost estimator
- ⬜ `eval-runner` — CLI to run any eval in this repo
- ⬜ `results-to-markdown` — turn results.json into a report table
- ⬜ `prompt-diff-viewer` — side-by-side prompt/version diff
- ⬜ `dataset-stats-dashboard` — small TUI/GUI dataset explorer
- ⬜ `jsonl-to-csv-converter` — robust format converter
- ⬜ `annotation-web-app` — small Flask app for labeling
- ⬜ `markdown-report-generator` — assemble a report from metrics
