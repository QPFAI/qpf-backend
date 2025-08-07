#!/usr/bin/env python3
"""
Adds emotional flourishes based on detected sentiment.
"""
def modulate_emotion(text: str, emotion: str) -> str:
    """
    Add emotional cues depending on emotion tag.

    Args:
        text: Current response text.
        emotion: 'positive', 'negative', or 'neutral'.
    Returns:
        Modified text with emotional flourish.
    """
    if emotion == "negative":
        return f"...{text} (I'm here for you)"
    if emotion == "positive":
        return f"{text}! 😊"
    return text
