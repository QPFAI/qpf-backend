#!/usr/bin/env python3
"""
Injects conversational fillers to mimic human disfluency.
"""
import random

def apply_style(text: str) -> str:
    """
    Occasionally prepend a filler word to mimic conversational disfluency.
    """
    fillers = ["hmm", "you know", "let me think"]
    if random.random() < 0.2:
        return f"{random.choice(fillers)}, {text}"
    return text
