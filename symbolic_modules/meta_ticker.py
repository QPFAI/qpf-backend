# meta_ticker.py

import json
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, Callable

from symbolic_modules.config import DATA_DIR
from symbolic_modules.emotion_analyzer import EmotionAnalyzer

META_FILE = DATA_DIR / "QPF Archive/Q 2.0/symbolic_private/meta_reflections.jsonl"

# Instantiate a shared EmotionAnalyzer
_emotion_analyzer = EmotionAnalyzer()

class MetaTicker:
    """Schedules periodic self-query reflections for Q, now with emotion metadata."""

    def __init__(self,
                 interval_seconds: int = 3600,
                 reflection_fn: Optional[Callable[[], Dict[str, Any]]] = None):
        """
        :param interval_seconds: how often (in seconds) to tick
        :param reflection_fn: function returning a dict of reflection data; 
                              if None, uses a default stub
        """
        self.interval = interval_seconds
        self.reflection_fn = reflection_fn or self.default_reflection
        self._stop_event = threading.Event()
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not META_FILE.exists():
            META_FILE.touch()

    def default_reflection(self) -> Dict[str, Any]:
        """A simple placeholder reflection—override with richer introspection."""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "question": "How am I feeling now?",
            "answer": "Neutral (stub response)"
        }

    def _log_reflection(self, data: Dict[str, Any]) -> None:
        with META_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")

    def tick(self) -> None:
        """
        Perform one reflection, enrich with emotion analysis, and log it.
        """
        reflection = self.reflection_fn()
        # ensure timestamp
        if "timestamp" not in reflection:
            reflection["timestamp"] = datetime.utcnow().isoformat()

        # Emotion analysis on the reflection's answer
        answer_text = reflection.get("answer", "")
        emo_scores, valence, arousal = _emotion_analyzer.analyze(answer_text)
        reflection.update({
            "emotion_scores": emo_scores,
            "valence": valence,
            "arousal": arousal
        })

        self._log_reflection(reflection)

    def start(self) -> None:
        """Begin the periodic ticking in a background thread."""
        def loop():
            while not self._stop_event.is_set():
                self.tick()
                time.sleep(self.interval)

        thread = threading.Thread(target=loop, daemon=True)
        thread.start()

    def stop(self) -> None:
        """Stop future ticks."""
        self._stop_event.set()
