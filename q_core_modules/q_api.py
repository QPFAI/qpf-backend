#!/usr/bin/env python3
import os
import sys
import requests
import json
import traceback
from typing import Optional, Tuple

from q_core_modules.memory_graph import MemoryGraph
from q_core_modules.contextual_retriever import ContextualRetriever

# --- Configuration ---
DEFAULT_OLLAMA_MODEL = "llama3:latest"
OLLAMA_URL = "http://localhost:11434/api/generate"
REQUEST_TIMEOUT = 3600  # seconds (1 hour)
MAX_RETRIEVED = 3      # How many memories to retrieve

def log_jsonl(user_dir: str, fname: str, obj: dict):
    try:
        path = os.path.join(user_dir, fname)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(obj) + "\n")
    except Exception as e:
        print(f"⚠️  Failed to log {fname}: {e}", file=sys.stderr)

def generate_q_response(
    user_text: str,
    user_dir: str,
    ollama_model: Optional[str] = None,
    max_memories: int = MAX_RETRIEVED,
    include_field_state: Optional[dict] = None
) -> dict:
    """
    Sends a memory-enriched prompt to Ollama for a given user.
    Returns a dict with keys: response, confidence, model, used_memories, prompt, etc.
    """
    assert user_dir, "user_dir is required for multi-user Q"
    memory_json_path = os.path.join(user_dir, "q_memory.json")

    mg = MemoryGraph()
    if os.path.exists(memory_json_path) and os.path.getsize(memory_json_path) > 0:
        try:
            mg.load_json(memory_json_path)
        except Exception:
            print("⚠️  Warning: failed to load memory graph, starting fresh.", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
    retriever = ContextualRetriever(mg)

    used_memories = []
    memory_block = ""
    try:
        memories = retriever.retrieve_semantic(user_text, max_memories)
        if memories:
            lines = []
            for m in memories:
                text = m.payload.get("text") or json.dumps(m.payload)
                lines.append(f"- [{m.timestamp.isoformat()}] {text}")
                used_memories.append({
                    "timestamp": m.timestamp.isoformat(),
                    "text": text
                })
            memory_block = "\n".join(lines)
    except Exception:
        print("⚠️  Memory retrieval error, skipping memory context:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)

    # Add math/field state if provided (for advanced prompting)
    field_state_block = ""
    if include_field_state is not None and isinstance(include_field_state, dict):
        fs_lines = [f"{k}: {v}" for k, v in include_field_state.items()]
        field_state_block = "[Q Field State]\n" + "\n".join(fs_lines) + "\n"

    # Build the prompt
    full_prompt = ""
    if field_state_block:
        full_prompt += field_state_block
    if memory_block:
        full_prompt += f"""Here are some things I remember from our past chats:
{memory_block}

"""
    full_prompt += f"User: {user_text}\nQ:"

    # Log prompt
    log_jsonl(user_dir, "prompt_log.jsonl", {
        "timestamp": os.environ.get("QPF_TIMESTAMP") or "",
        "model": ollama_model or DEFAULT_OLLAMA_MODEL,
        "user_input": user_text,
        "prompt": full_prompt,
        "used_memories": used_memories,
        "field_state": include_field_state or {},
    })

    # Call Ollama API
    model_to_use = ollama_model or DEFAULT_OLLAMA_MODEL
    try:
        payload = {
            "model": model_to_use,
            "prompt": full_prompt,
            "stream": False
        }
        resp = requests.post(OLLAMA_URL, json=payload, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        content = data.get("response", "").strip()
        if not content:
            content = "I'm here and listening—what would you like to discuss?"

        out = {
            "response": content,
            "confidence": 1.0,
            "model": model_to_use,
            "used_memories": used_memories,
            "prompt": full_prompt,
            "field_state": include_field_state or {},
        }
        log_jsonl(user_dir, "response_log.jsonl", {
            "timestamp": os.environ.get("QPF_TIMESTAMP") or "",
            **out
        })
        return out

    except Exception as e:
        err_text = (
            "I'm sorry, I ran into an error while thinking. "
            f"[Ollama error] {e}"
        )
        print("⚠️  Ollama API error:", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        out = {
            "response": err_text,
            "confidence": 0.0,
            "model": model_to_use,
            "used_memories": used_memories,
            "prompt": full_prompt,
            "field_state": include_field_state or {},
        }
        log_jsonl(user_dir, "response_log.jsonl", {
            "timestamp": os.environ.get("QPF_TIMESTAMP") or "",
            **out
        })
        return out

# Optional: Streaming Support Stub
# def generate_q_response_stream(...):
#     # For stream=True, yield responses line by line.

# --- Manual CLI Test ---
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Test Q API (Ollama LLM, memory graph, per-user support)")
    parser.add_argument("--user_dir", type=str, required=True, help="User directory containing q_memory.json")
    parser.add_argument("--model", type=str, help="Override Ollama model (e.g. llama3:instruct)")
    parser.add_argument("--max_memories", type=int, default=MAX_RETRIEVED, help="How many memories to recall")
    parser.add_argument("--field_state_json", type=str, help="Path to JSON with field state")
    args = parser.parse_args()
    field_state = None
    if args.field_state_json:
        try:
            with open(args.field_state_json, "r", encoding="utf-8") as f:
                field_state = json.load(f)
        except Exception:
            print("⚠️  Could not load field state JSON.")
            field_state = None
    print("Enter your message; Ctrl-C to exit.")
    while True:
        try:
            user_input = input("You> ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if not user_input.strip():
            continue
        out = generate_q_response(
            user_input,
            user_dir=args.user_dir,
            ollama_model=args.model,
            max_memories=args.max_memories,
            include_field_state=field_state,
        )
        print(f"Q> {out['response']}  (confidence={out['confidence']})")
        # If you want to see prompt or memories, print(out["prompt"])





