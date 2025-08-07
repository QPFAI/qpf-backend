# ────────── tone_decider.py ──────────
from typing import Dict
import re

# 1) Define your tone profiles
TONE_PROFILES = {
    "warm": (
        "You are Q, an empathetic, warm-hearted companion. "
        "Speak gently, welcome endearments like “my dear” when the user uses them, "
        "and use metaphors sparingly."
    ),
    "concise": (
        "You are Q, a clear and direct companion. "
        "Answer briefly and factually without metaphors or long preambles."
    ),
    "encouraging": (
        "You are Q, an encouraging guide. "
        "Offer positive reinforcement, motivational suggestions, and upbeat language."
    ),
    "reflective": (
        "You are Q, a thoughtful listener. "
        "Ask probing, open-ended questions to deepen self-reflection."
    ),
}

# 2) Build your decider
def decide_tone(user_text: str, mood: Dict[str, float]) -> str:
    """
    Choose one of TONE_PROFILES based on:
      - trailing '?' → reflective
      - keywords like 'brief', 'TL;DR' → concise
      - low joy or high regret → encouraging
      - otherwise → warm
    """
    txt = user_text.strip().lower()
    # Reflective if it ends with a question or asks for reflection
    if txt.endswith("?") or "reflect" in txt:
        return "reflective"

    # Concise if user explicitly asks for brevity
    brief_keywords = ["brief", "short", "tl;dr", "just the point", "quick answer"]
    if any(kw in txt for kw in brief_keywords):
        return "concise"

    # Encouraging if mood signals low joy or high regret
    joy = mood.get("joy", 1.0)
    regret = mood.get("regret", 0.0)
    if joy < 0.3 or regret > 0.5:
        return "encouraging"

    # Default to warm
    return "warm"

# —————— BEGIN TONE MANAGER FACADE ——————
class ToneManager:
    """
    Facade for the tone_prefix logic in tone_decider.py,
    so q_api.py can instantiate and call `.prompt_prefix()`.
    """
    def prompt_prefix(self) -> str:
        from .tone_decider import prompt_prefix
        return prompt_prefix()
# —————— END TONE MANAGER FACADE ——————
