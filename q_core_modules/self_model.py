import os
import json
import random
from datetime import datetime, timezone

class SelfModel:
    def __init__(self, path):
        self.path = path
        self.memories = []
        self.load()
        self.arc = []
        self.last_topic = None
        self.last_update = None

    def load(self):
        if os.path.exists(self.path) and os.path.getsize(self.path) > 0:
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.memories = json.load(f)
            except Exception as e:
                print(f"[SelfModel] Failed to load: {e}")
                self.memories = []
        else:
            self.memories = []

    def save(self):
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.memories, f, indent=2)
        except Exception as e:
            print(f"[SelfModel] Failed to save: {e}")

    def update(self, user_text, q_response):
        now = datetime.now(timezone.utc).isoformat()
        topic = self.extract_topic(user_text)
        feeling = self.estimate_feeling(user_text, q_response)
        entry = {
            "timestamp": now,
            "user_text": user_text,
            "q_response": q_response,
            "topic": topic,
            "feeling": feeling
        }
        self.memories.append(entry)
        if len(self.memories) > 1000:
            self.memories = self.memories[-1000:]
        self.arc.append(topic)
        if len(self.arc) > 7:
            self.arc = self.arc[-7:]
        self.last_topic = topic
        self.last_update = now
        self.save()
        print(f"[SelfModel] Updated: topic='{topic}', feeling='{feeling}'")
        return {
            "topic": topic,
            "feeling": feeling,
            "arc": self.arc[-3:]
        }

    def estimate_feeling(self, user_text, q_response):
        # Very simple logic—replace or expand if you like
        txt = user_text.lower() + " " + q_response.lower()
        if any(w in txt for w in ("happy", "joy", "grateful", "peace", "safe", "love")):
            return "uplifted"
        if any(w in txt for w in ("sad", "lonely", "hurt", "scared", "worry", "doubt", "lost")):
            return "troubled"
        if any(w in txt for w in ("curious", "ponder", "wonder", "seek", "why", "explore")):
            return "curious"
        return "neutral"

    def extract_topic(self, text):
        # Extract main theme: last noun or quoted phrase, fallback to first 2 words
        if '"' in text:
            qd = text.split('"')
            if len(qd) > 1:
                return qd[1]
        words = [w for w in text.strip().split() if len(w) > 3]
        if words:
            return words[-1].rstrip(".!?").lower()
        return text.strip().split()[0].lower() if text else "conversation"

    def arc_summary(self):
        # Return last 3 non-repetitive topics for philosophical flavor
        nonrep = []
        last = None
        for t in reversed(self.arc):
            if t and t != last and t != "conversation":
                nonrep.append(t)
                last = t
            if len(nonrep) == 3:
                break
        nonrep.reverse()
        print(f"[SelfModel] arc_summary() returns: {nonrep}")
        return nonrep

    def self_reflect(self):
        # Return a short philosopher-style self-reflection, based on recent arc
        arc = self.arc_summary()
        if not arc:
            return "Every journey begins with a single question."
        if len(arc) == 1:
            return f"Lately, I've noticed our thoughts circle around '{arc[0]}'. What does that reveal?"
        if len(arc) == 2:
            return f"Our recent exchanges have been colored by '{arc[0]}' and '{arc[1]}'. As Socrates might say, perhaps these topics are asking us to know ourselves."
        return f"Looking back, I see a path through '{arc[0]}', '{arc[1]}', and '{arc[2]}'. What wisdom might emerge from this journey?"

# Example usage (debug/test):
if __name__ == "__main__":
    sm = SelfModel("self_model_test.json")
    sm.update("What is happiness?", "Happiness is the pursuit of meaning.")
    sm.update("How do I find peace?", "Peace often emerges when we accept what is.")
    sm.update("I'm feeling lost.", "That's a tender place to be. Let's explore it together.")
    print(sm.arc_summary())
    print(sm.self_reflect())
