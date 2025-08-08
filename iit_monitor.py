import collections
import collections.abc
# Monkey‐patch so PyPhi’s old imports work under Python 3.13+
collections.Iterable = collections.abc.Iterable
collections.Sequence = collections.abc.Sequence
collections.Mapping  = collections.abc.Mapping

import threading
import time
import pyphi

# ─── PyPhi Thread‐Safe Configuration ───────────────────────────────
# Disable all parallel evaluation steps in PyPhi
pyphi.config.PARALLEL_CONCEPT_EVALUATION = False   # disable parallel concept finding :contentReference[oaicite:0]{index=0}
pyphi.config.PARALLEL_CUT_EVALUATION     = False   # disable parallel cut evaluation :contentReference[oaicite:1]{index=1}
pyphi.config.PARALLEL_COMPLEX_EVALUATION = False   # disable parallel complex evaluation :contentReference[oaicite:2]{index=2}
# Turn off progress bars for cleaner logs
pyphi.config.PROGRESS_BARS = False                # disable tqdm-style progress bars :contentReference[oaicite:3]{index=3}

from q_core_modules.network import NETWORK                    # your local network.py
from pyphi.compute.subsystem import phi        # the core Φ function

def get_state_vector():
    """
    Placeholder: returns a zero-vector for NETWORK.size.
    Replace this with your real sensor/variable sampling logic.
    """
    return [0] * NETWORK.size

def log_phi(phi_value):
    """Handle or persist the computed Φ value."""
    print(f"[Φ] Computed Φ: {phi_value}")

def sample_phi():
    print("[Φ] sample_phi called")  # Debug log

    state_vector = get_state_vector()
    print(f"[Φ] State vector: {state_vector} (len={len(state_vector)})")
    print(f"[Φ] NETWORK.size: {NETWORK.size}")

    expected = NETWORK.size
    actual   = len(state_vector)
    if actual != expected:
        raise RuntimeError(
            f"IIT error: expected {expected} state entries, "
            f"but got {actual}: {state_vector}"
        )

    subsystem = pyphi.Subsystem(NETWORK, state_vector)
    phi_value = phi(subsystem)
    log_phi(phi_value)

def start_periodic_sampling(interval_seconds: float = 10.0):
    """
    Launch a daemon thread that runs sample_phi() every `interval_seconds`.
    """
    def loop():
        while True:
            try:
                sample_phi()
            except Exception as e:
                import traceback
                print(f"[iit_monitor] Exception: {e}")
                traceback.print_exc()
            print(f"[Φ] Looping again in {interval_seconds} seconds\n")
            time.sleep(interval_seconds)

    thread = threading.Thread(target=loop, name="IIT-Monitor", daemon=True)
    thread.start()
    return thread

# ─── Manual Test Runner ───────────────────────────────────────────
if __name__ == "__main__":
    print("Manual one-shot Φ calculation:")
    sample_phi()
    print("Starting continuous periodic Φ sampling (Ctrl+C to exit)...")
    start_periodic_sampling(10)
    while True:
        time.sleep(60)




