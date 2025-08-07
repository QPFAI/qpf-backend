# counterfactual.py

import copy
import threading
import time
import json
from datetime import datetime
from typing import Dict, Any, List

from .memory_graph import MemoryGraph, MemoryEvent

class CounterfactualEngine:
    """
    Clone the current MemoryGraph state, apply modifier sets,
    simulate one collapse per branch, then compare outcomes.
    """
    def __init__(self, mg: MemoryGraph, log_path: str):
        self.mg = mg
        self.log_path = log_path

    def clone_state(self) -> MemoryGraph:
        """Deep-copy the MemoryGraph (including nodes & edges)."""
        mg_copy = copy.deepcopy(self.mg)
        return mg_copy

    def run_branch(self,
                   modifiers: Dict[str, float],
                   base_event: MemoryEvent = None
                  ) -> Dict[str, Any]:
        """
        Run one counterfactual branch:
        - clone the state
        - optionally inject or tweak anchors per modifiers
        - simulate one collapse (stubbed as adding a MemoryEvent)
        - compute a simple score (e.g. average valence in last N events)
        Returns a dict of { 'modifiers':…, 'score':…, 'timestamp':… }.
        """
        mg_copy = self.clone_state()

        # 1) Inject anchor modifications
        for anchor, delta in modifiers.items():
            ev = MemoryEvent(
                type="anchor_tweak",
                payload={"anchor": anchor, "delta": delta}
            )
            mg_copy.add_event(ev)

        # 2) Simulate a collapse (stub – replace with your actual collapse logic)
        collapse_ev = MemoryEvent(type="collapse", payload={"counterfactual": True})
        mg_copy.add_event(collapse_ev)

        # 3) Score the branch: e.g. count 'valence' in payloads if present
        vals = [
            ev.payload.get("valence", 0.0)
            for _, data in mg_copy.graph.nodes(data=True)
            for ev in [data["event"]]
            if "valence" in ev.payload
        ]
        score = sum(vals) / (len(vals) or 1)

        result = {
            "timestamp": datetime.utcnow().isoformat(),
            "modifiers": modifiers,
            "score": score
        }

        # 4) Log to file
        with open(self.log_path, "a") as f:
            f.write(json.dumps(result) + "\n")

        return result

    def batch_run(self,
                  modifier_sets: List[Dict[str, float]]
                 ) -> List[Dict[str, Any]]:
        """
        Run multiple branches in sequence and return all results.
        """
        results = []
        for mods in modifier_sets:
            results.append(self.run_branch(mods))
        return results

    def start_nightly(self,
                      modifier_sets: List[Dict[str, float]],
                      start_hour: int = 22,
                      end_hour: int = 6,
                      interval_seconds: int = 3600
                     ):
        """
        Launch a daemon thread that, between start_hour and end_hour,
        runs batch_run(modifier_sets) every interval_seconds.
        """
        def _loop():
            while True:
                now = datetime.utcnow()
                # hour in UTC—adjust if needed for local time
                h = now.hour
                if (start_hour <= h < 24) or (0 <= h < end_hour):
                    self.batch_run(modifier_sets)
                time.sleep(interval_seconds)

        t = threading.Thread(target=_loop, daemon=True)
        t.start()
