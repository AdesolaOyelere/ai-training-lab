# Edge-Case Catalog — Sentiment Annotation

The main sentiment guideline covers the common cases. This catalog covers the *edge*
cases — the patterns where annotators disagree most — and tells you how to handle each.
The detectors in `catalog.py` flag these patterns automatically so the annotation tool
can surface the right rule; the annotator still assigns the final label.

## The cases

### 1. Negation
A polarity word is negated, flipping its meaning. "I do **not** like it" is negative
even though "like" is positive.
**Rule:** resolve the negation before labeling; label the *resulting* sentiment, not the
polarity word in isolation.

### 2. Contrast / mixed
Two opposing sentiments joined by "but", "however", "although". "The food was good
**but** the service was terrible."
**Rule:** these are genuinely mixed. Follow the project's mixed-sentiment convention
(here: label `mixed`, do not average to neutral).

### 3. Sarcasm cue
Positive words used to mean the opposite, often with a cue like "oh great", "just what
I needed", or scare quotes.
**Rule:** if context makes the sarcasm clear, label the *intended* sentiment (usually
negative). If it is ambiguous, flag for adjudication rather than guessing.

### 4. Comparison
Sentiment expressed relative to something else — "better than my old one".
**Rule:** label the sentiment toward the **subject** of the review, not the comparison
target. "Better than my old one" is positive about the new item.

### 5. Rhetorical question
A question not seeking information, often carrying sentiment — "Who would ever want
this?"
**Rule:** interpret the implied statement ("no one would want this" → negative). Do not
label rhetorical questions as neutral by default.

### 6. Conditional
Sentiment tied to an unmet condition — "I **would have** loved it **if** it were
cheaper."
**Rule:** the condition was not met, so the expressed sentiment about the actual
product is usually negative or disappointed, not the hypothetical positive.

## Using the detector

`detect_edge_cases(text)` returns which of these apply; `needs_careful_review(text)` is
true if any do. `gold_examples.json` pins the correct routing for a set of examples, and
the tests verify the detector reproduces it — so the catalog and the code stay in sync.
