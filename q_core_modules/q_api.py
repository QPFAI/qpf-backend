#!/usr/bin/env python3
import os
import sys
import requests
import json
import traceback

from q_core_modules.tone_decider import ToneManager
from .memory_graph import MemoryGraph
from .contextual_retriever import ContextualRetriever

# ─── Configuration ─────────────────────────────────────────────────────────────
OLLAMA_MODEL    = "llama3:latest"
OLLAMA_URL      = "http://localhost:11434/api/generate"
REQUEST_TIMEOUT = 120  # seconds

# ─── Initialize ToneManager ────────────────────────────────────────────────────
_tm = ToneManager()

# ─── Load MemoryGraph & Retriever ──────────────────────────────────────────────
BASE_DIR          = os.path.dirname(os.path.abspath(__file__))
MEMORY_JSON_PATH  = os.path.join(BASE_DIR, "q_memory.json")

mg = MemoryGraph()
if os.path.exists(MEMORY_JSON_PATH) and os.path.getsize(MEMORY_JSON_PATH) > 0:
    try:
        mg.load_json(MEMORY_JSON_PATH)
    except Exception:
        # If loading fails for any reason, start with an empty graph
        print("⚠️  Warning: failed to load memory graph, starting fresh.", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

retriever = ContextualRetriever(mg)

def generate_q_response(user_text: str) -> tuple[str, float]:
    """
    Sends a styled, memory-enriched prompt to Ollama.
    Returns (response_text, confidence_score).
    """
    # 1) Get the caring style instruction
    style = _tm.prompt_prefix()

    # 2) Try to fetch up to 3 relevant past memories
    memory_block = ""
    try:
        memories = retriever.retrieve_semantic(user_text, 3)
        if memories:
            lines = []
            for m in memories:
                text = m.payload.get("text") or json.dumps(m.payload)
                lines.append(f"- [{m.timestamp.isoformat()}] {text}")
            memory_block = "\n".join(lines)
    except Exception:
        print("⚠️  Memory retrieval error, skipping memory context:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

    # 3) Build the full prompt
    if memory_block:
        full_prompt = f"""{style}

Here are some things I remember from our past chats:
{memory_block}

User: {user_text}
Q:"""
    else:
        full_prompt = f"""{style}

User: {user_text}
Q:"""

    # 4) Call the Ollama HTTP API
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": full_prompt,
            "stream": False
        }
        resp = requests.post(OLLAMA_URL, json=payload, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        content = data.get("response", "").strip()
        if not content:
            content = "I'm here and listening—what would you like to discuss?"
        return content, 1.0

    except Exception as e:
        err_text = (
            "I'm sorry, I ran into an error while thinking. "
            f"[Ollama error] {e}"
        )
        print("⚠️  Ollama API error:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        return err_text, 0.0

# ─── Allow quick manual testing ─────────────────────────────────────────────────
if __name__ == "__main__":
    print("Enter your message; Ctrl-C to exit.")
    while True:
        try:
            user_input = input("You> ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if not user_input.strip():
            continue
        resp, conf = generate_q_response(user_input)
        print(f"Q> {resp}  (confidence={conf})")



