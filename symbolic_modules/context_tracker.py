import json
import os
from pathlib import Path
from datetime import datetime

# Set your symbolic_private directory
SYMBOLIC_PRIVATE_DIR = "/Volumes/QPF Archive/Q 2.0/symbolic_private"
CONTEXT_LOG = os.path.join(SYMBOLIC_PRIVATE_DIR, "session_context.jsonl")

os.makedirs(SYMBOLIC_PRIVATE_DIR, exist_ok=True)  # Ensure the folder exists

def track_context(message: str):
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "message": message
    }
    with open(CONTEXT_LOG, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def get_recent_context(limit: int = 20):
    entries = []
    try:
        with open(CONTEXT_LOG, "r", encoding="utf-8") as f:
            lines = f.readlines()[-limit:]
        entries = [json.loads(l) for l in lines if l.strip()]
    except Exception:
        pass
    return entries

