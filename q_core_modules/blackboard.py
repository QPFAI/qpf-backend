#!/usr/bin/env python3
"""
symbolic_modules/blackboard.py
"""

from collections import defaultdict
import fnmatch

# Registry mapping event patterns → list of listener callables
_subscribers: dict[str, list[callable]] = defaultdict(list)

def subscribe(event_pattern: str, fn: callable):
    """
    Register fn to be called whenever an event matching event_pattern is published.
    Wildcards '*' and '?' are supported in the pattern.
    fn signature should be fn(event_type: str, payload: dict).
    """
    _subscribers[event_pattern].append(fn)


def publish(event_type: str, payload: dict):
    """
    Notify all subscribers whose pattern matches this event_type.
    Each listener is called with (event_type, payload).
    """
    for pattern, listeners in _subscribers.items():
        if fnmatch.fnmatch(event_type, pattern):
            for fn in listeners:
                try:
                    fn(event_type, payload)
                except Exception as e:
                    print(f"⚠ Blackboard listener error in {fn.__name__}: {e}")


# —————— BEGIN FACADE CLASS ——————
class Blackboard:
    """Facade for symbolic_modules.blackboard functionality with wildcard support."""
    def __init__(self):
        # Allow delegation to module‐level subscribe/publish
        from . import blackboard as _mod
        self._mod = _mod

    def subscribe(self, pattern: str, fn: callable):
        return self._mod.subscribe(pattern, fn)

    def publish(self, event_type: str, payload: dict):
        return self._mod.publish(event_type, payload)
# —————— END FACADE CLASS ——————
