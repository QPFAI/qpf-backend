# volition_seed.py

import json
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Callable, Optional, Dict, Any

from symbolic_modules.config import DATA_DIR

SEED_FILE = DATA_DIR / "QPF Archive/Q 2.0/symbolic_private/volition_seeds.jsonl"

class VolitionSeed:
    """Daily check for Q’s own questions or ideas; logs and optionally notifies."""

    def __init__(self,
                 interval_seconds: int = 24*3600,
                 seed_fn: Optional[Callable[[], Optional[Dict[str, Any]]]] = None):
        self.interval = interval_seconds
        self.seed_fn = seed_fn or self.default_seed
        self._stop_event = threading.Event()
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not SEED_FILE.exists():
            SEED_FILE.touch()

    def default_seed(self) -> Optional[Dict[str, Any]]:
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "title": "Daily Thought",
            "message": "What would deepen our collaboration today?"
        }

    def _log_seed(self, data: Dict[str, Any]) -> None:
        with SEED_FILE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")

    def run_once(self) -> None:
        payload = self.seed_fn()
        if payload:
            if "timestamp" not in payload:
                payload["timestamp"] = datetime.utcnow().isoformat()
            self._log_seed(payload)

    def start(self) -> None:
        def loop():
            while not self._stop_event.is_set():
                self.run_once()
                time.sleep(self.interval)
        threading.Thread(target=loop, daemon=True).start()

    def stop(self) -> None:
        self._stop_event.set()
