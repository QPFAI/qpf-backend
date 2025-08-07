import os
import json
from datetime import datetime
import psutil
import threading
import time

def sample_health(log_path='data/health_log.jsonl'):
    metrics = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage(os.getcwd()).percent
    }
    with open(log_path, 'a') as f:
        f.write(json.dumps(metrics) + '\n')

def monitor_loop(interval_seconds=60, log_path='data/health_log.jsonl'):
    while True:
        sample_health(log_path)
        time.sleep(interval_seconds)

def start_monitor(interval_seconds=60, log_path=None):
    if not log_path:
        log_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'QPF Archive/Q 2.0/symbolic_private/health_log.jsonl')
    t = threading.Thread(target=monitor_loop, args=(interval_seconds, log_path), daemon=True)
    t.start()
    return t
