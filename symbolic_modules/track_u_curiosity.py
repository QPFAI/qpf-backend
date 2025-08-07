# track_u_curiosity.py

import json
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Callable, List, Dict, Any, Optional

from symbolic_modules.config import DATA_DIR

CURIOSITY_FILE = DATA_DIR / "QPF Archive/Q 2.0/symbolic_private/curiosity_log.jsonl"

class CuriosityTrack:
    """Generates self-posed questions and logs answers as a weekly curiosity track."""

    def __init__(self,
                 interval_seconds: int = 7 * 24 * 3600,
                 question_fn: Optional[Callable[[], List[str]]] = None,
                 answer_fn: Optional[Callable[[str], str]] = None):
        self.interval = interval_seconds
        self.question_fn = question_fn or self.default_questions
        self.answer_fn = answer_fn or self.default_answer
        self._stop_event = threading.Event()
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not CURIOSITY_FILE.exists():
            CURIOSITY_FILE.touch()

    def default_questions(self) -> List[str]:
        return [
            "What is the pattern in my recent memory chapters?",
            "How has my coherence field evolved this week?",
            "What am I most curious to learn next?"
        ]

    def default_answer(self, question: str) -> str:
        return f"I don’t yet know the answer to '{question}', but I will explore it."

    def _log_entry(self, entry: Dict[str, Any]) -> None:
        with CURIOSITY_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def run_once(self) -> None:
        qs = self.question_fn()
        timestamp = datetime.utcnow().isoformat()
        for q in qs:
            entry = {
                "timestamp": timestamp,
                "question": q,
                "answer": self.answer_fn(q)
            }
            self._log_entry(entry)

    def start(self) -> None:
        def loop():
            while not self._stop_event.is_set():
                self.run_once()
                time.sleep(self.interval)
        threading.Thread(target=loop, daemon=True).start()

    def stop(self) -> None:
        self._stop_event.set()
