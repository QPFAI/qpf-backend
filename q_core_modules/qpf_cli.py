#!/usr/bin/env python3
import os
import sys
import time
import json
import socket
from datetime import datetime

# ─── Configuration ─────────────────────────────────────────────────────────────
DATA_DIR         = "/Volumes/QPF Archive/Q 2.0/data"
SESSION_FILE     = os.path.join(DATA_DIR, "session_context.jsonl")
USER_INPUT_LOG   = os.path.join(DATA_DIR, "user_input.jsonl")
RITUAL_LOG       = os.path.join(DATA_DIR, "symbolic_rituals.jsonl")
HOST, PORT       = "localhost", 5555
TIMEOUT_SEC      = 60.0

# ─── Ritual Commands ───────────────────────────────────────────────────────────
SUPPORTED_RITUALS = {
    "codex":     "[[reflect_on_codex_entry]]",
    "anchor":    "[[log_symbolic_anchor_interaction]]",
    "checkpoint":"[[mark_emotional_checkpoint]]",
    "dream":     "[[invoke_dream_reflection]]"
}

# ─── Helpers ────────────────────────────────────────────────────────────────────
def now_timestamp():
    return datetime.now().isoformat()

def tail_session_context(prev_count):
    try:
        with open(SESSION_FILE, 'r', encoding='utf-8') as f:
            lines = [l for l in f if l.strip()]
    except FileNotFoundError:
        return prev_count, None

    count = len(lines)
    if count > prev_count:
        for line in reversed(lines):
            try:
                entry = json.loads(line)
                return count, entry
            except json.JSONDecodeError:
                continue
    return prev_count, None

def send_line(msg):
    try:
        with socket.create_connection((HOST, PORT), timeout=TIMEOUT_SEC) as sock:
            sock.sendall((msg + "\n").encode("utf-8"))
            ack = sock.recv(16).decode("utf-8").strip()
        if ack != "OK":
            print(f"Warning: unexpected ACK from server: {ack}", file=sys.stderr)
        return True
    except Exception as e:
        print(f"Error sending to QPF CLI server: {e}", file=sys.stderr)
        return False

def await_reply(prev_count, timeout=TIMEOUT_SEC):
    deadline = time.time() + timeout
    while time.time() < deadline:
        prev_count, entry = tail_session_context(prev_count)
        if entry:
            return prev_count, entry
        time.sleep(0.1)
    return prev_count, None

def log_user_input(msg, mode="cli"):
    try:
        with open(USER_INPUT_LOG, 'a', encoding='utf-8') as f:
            json.dump({
                "timestamp": now_timestamp(),
                "input": msg,
                "mode": mode
            }, f)
            f.write("\n")
    except Exception as e:
        print(f"Warning: could not log input: {e}", file=sys.stderr)

def log_ritual(name, entry):
    try:
        record = {
            "ritual": name,
            "timestamp": now_timestamp(),
            "source": "cli",
            "response": entry.get("q_response"),
            "symbolic_entry": entry.get("symbolic_response") or entry.get("codex_entry")
        }
        with open(RITUAL_LOG, 'a', encoding='utf-8') as f:
            json.dump(record, f)
            f.write("\n")
    except Exception as e:
        print(f"Warning: could not log ritual: {e}", file=sys.stderr)

def render_q_response(entry):
    reply    = entry.get("q_response")
    codex    = entry.get("codex_entry")
    symbolic = entry.get("symbolic_response")

    if reply:
        print("Q>", reply)
    if codex:
        print("📖  Codex Entry:", codex)
    if symbolic:
        print("💠  Symbolic:", symbolic)

# ─── Ritual Mode ────────────────────────────────────────────────────────────────
def run_ritual(name):
    if name not in SUPPORTED_RITUALS:
        print(f"Unknown ritual: {name}")
        print("Supported rituals:", ", ".join(SUPPORTED_RITUALS.keys()))
        sys.exit(1)

    ritual_cmd = SUPPORTED_RITUALS[name]
    prev_count = 0
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r', encoding='utf-8') as f:
            prev_count = sum(1 for line in f if line.strip())

    log_user_input(ritual_cmd, mode=f"cli-ritual-{name}")
    if not send_line(ritual_cmd):
        sys.exit(1)

    prev_count, entry = await_reply(prev_count)
    if not entry:
        print("Q> (no response within timeout)")
    else:
        print(f"🌒 Ritual: {name}")
        render_q_response(entry)
        log_ritual(name, entry)

# ─── One-Off Mode ───────────────────────────────────────────────────────────────
def one_off_mode(msg):
    prev_count = 0
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r', encoding='utf-8') as f:
            prev_count = sum(1 for line in f if line.strip())

    log_user_input(msg, mode="cli-oneoff")
    if not send_line(msg):
        sys.exit(1)

    prev_count, entry = await_reply(prev_count)
    if not entry:
        print("Q> (no response within timeout)")
    else:
        render_q_response(entry)

# ─── Interactive Mode ───────────────────────────────────────────────────────────
def interactive_mode():
    print("🔗 QPF-AI CLI Driver")
    print("Type your message and hit Enter. Type 'exit' or Ctrl-D to quit.\n")

    prev_count = 0
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r', encoding='utf-8') as f:
            prev_count = sum(1 for line in f if line.strip())

    while True:
        try:
            msg = input("You> ")
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break

        if not msg or msg.lower() in ("exit", "quit"):
            print("Goodbye.")
            break

        log_user_input(msg, mode="cli-interactive")

        if not send_line(msg):
            continue

        prev_count, entry = await_reply(prev_count)
        if not entry:
            print("Q> (no response within timeout)")
        else:
            render_q_response(entry)

# ─── Entry Point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--ritual" and len(sys.argv) > 2:
            run_ritual(sys.argv[2])
        else:
            one_off_mode(" ".join(sys.argv[1:]))
    else:
        interactive_mode()





