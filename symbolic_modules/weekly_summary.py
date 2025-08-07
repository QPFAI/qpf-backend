import threading
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
import json

class WeeklySummary:
    def __init__(self, interval_days=7, data_dir: Path = None):
        # Always use the symbolic_private folder
        self.data_dir = Path("/Volumes/QPF Archive/Q 2.0/symbolic_private")
        self.interval = interval_days
        self._thread = threading.Thread(target=self._loop, daemon=True)

    def start(self):
        self._thread.start()

    def _loop(self):
        while True:
            try:
                self.summarize()
            except Exception as e:
                print(f"WeeklySummary error: {e}")
            time.sleep(self.interval * 24 * 3600)

    def summarize(self):
        # Load session_context to build a weekly summary
        session_file = self.data_dir / "session_context.jsonl"
        if not session_file.exists():
            return

        now = datetime.now(timezone.utc)
        since = now - timedelta(days=self.interval)

        entries = []
        with open(session_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    c = json.loads(line)
                    raw_ts = c.get("timestamp")
                    ts = datetime.fromisoformat(raw_ts)
                    # ensure timezone-aware
                    if ts.tzinfo is None:
                        ts = ts.replace(tzinfo=timezone.utc)
                    if ts >= since:
                        entries.append(c)
                except Exception:
                    continue

        # Produce a simple summary
        summary_text = f"Weekly Summary ({since.date()} to {now.date()}):\n"
        summary_text += f"- {len(entries)} interactions recorded.\n"

        # Write to the symbolic_private folder
        summary_file = self.data_dir / "weekly_summary.txt"
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(summary_text)

        # Optionally publish to workspace (if you want)
        try:
            from symbolic_modules.global_workspace import workspace
            workspace.publish("weekly_summary", {"text": summary_text})
        except ImportError:
            pass



