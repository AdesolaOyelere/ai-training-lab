"""Deterministic intent-classification data for the ablation.

Three intents (greeting, weather, farewell). The train list is ordered so that the
first few exemplars already cover the intents, which is what lets the few-shot curve
rise quickly and reproducibly.
"""

TRAIN = [
    {"text": "hello there how are you", "label": "greeting"},
    {"text": "what is the weather like today", "label": "weather"},
    {"text": "goodbye see you later", "label": "farewell"},
    {"text": "hi good morning to you", "label": "greeting"},
    {"text": "will it rain tomorrow", "label": "weather"},
    {"text": "bye take care now", "label": "farewell"},
    {"text": "hey nice to meet you", "label": "greeting"},
    {"text": "is it sunny outside right now", "label": "weather"},
    {"text": "see you soon farewell", "label": "farewell"},
]

TEST = [
    {"text": "hello good to see you", "label": "greeting"},
    {"text": "how is the weather outside", "label": "weather"},
    {"text": "goodbye for now", "label": "farewell"},
    {"text": "hi there friend", "label": "greeting"},
    {"text": "will it be sunny tomorrow", "label": "weather"},
    {"text": "bye see you later", "label": "farewell"},
]
