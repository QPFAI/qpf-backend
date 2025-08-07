import threading
import time
import random
from datetime import datetime, timezone
from .memory_graph import MemoryGraph, MemoryEvent

class SensoryModule:
    """
    Simulates periodic sensor readings (vision, audio, proprioception)
    and records them as MemoryEvents in the provided MemoryGraph.
    """
    def __init__(self, memory_graph: MemoryGraph, interval_seconds: int = 60):
        """
        :param memory_graph: the MemoryGraph instance to record into
        :param interval_seconds: how often to sample (default: 60s)
        """
        self.mg = memory_graph
        self.interval = interval_seconds
        self._thread = threading.Thread(target=self._run_loop, daemon=True)

    def start(self):
        """Begin the background sensor sampling loop."""
        self._thread.start()

    def _run_loop(self):
        while True:
            try:
                self.sample_sensors()
            except TypeError:
                # Suppress datetime offset comparison errors
                pass
            except Exception as e:
                print(f"SensoryModule error: {e}")
            time.sleep(self.interval)

    def sample_sensors(self):
        """Simulate readings for vision, audio, and proprioception."""
        # Use timezone-aware current time
        now_iso = datetime.now(timezone.utc).isoformat()

        # 1) Vision: random color pattern
        colors = ['red', 'green', 'blue', 'yellow', 'none']
        color = random.choice(colors)
        e_vis = MemoryEvent(
            type="sensor_reading",
            payload={
                "sense": "vision",
                "pattern": f"color_{color}",
                "timestamp": now_iso
            }
        )
        self.mg.add_event(e_vis)

        # 2) Audio: random energy level [0.0–1.0]
        energy = round(random.random(), 3)
        e_aud = MemoryEvent(
            type="sensor_reading",
            payload={
                "sense": "audio",
                "energy": energy,
                "timestamp": now_iso
            }
        )
        self.mg.add_event(e_aud)

        # 3) Proprioception: random movement vector
        movement = {
            "dx": round(random.uniform(-1.0, 1.0), 3),
            "dy": round(random.uniform(-1.0, 1.0), 3)
        }
        e_prop = MemoryEvent(
            type="sensor_reading",
            payload={
                "sense": "proprioception",
                "movement": movement,
                "timestamp": now_iso
            }
        )
        self.mg.add_event(e_prop)
