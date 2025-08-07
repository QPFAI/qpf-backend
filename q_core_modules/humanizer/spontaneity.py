#!/usr/bin/env python3
"""
Occasionally adds a playful aside for spontaneity.
"""
import random

def maybe_spontaneity(text: str) -> str:
    """
    With low probability, append a playful comment.
    """
    if random.random() < 0.1:
        return f"{text}\nBy the way, did you know I love learning new things?"
    return text
