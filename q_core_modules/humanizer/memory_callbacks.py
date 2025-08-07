#!/usr/bin/env python3
"""
Appends a brief callback referencing the most recent memory event.
"""
from q_core_modules.memory_graph import MemoryEvent

def inject_memory_callbacks(text: str, mg) -> str:
    """
    Append a reminder of the last memory event if available.

    Args:
        text: Current response text.
        mg: MemoryGraph instance.
    Returns:
        Modified text with memory callback.
    """
    events = mg.retrieve(lambda e: True, max_results=1)
    if events:
        last = events[0]
        snippet = last.payload.get("text", "").strip()
        if snippet:
            truncated = (snippet[:50] + '...') if len(snippet) > 50 else snippet
            return f"{text} (I remember you said: '{truncated}')"
    return text
