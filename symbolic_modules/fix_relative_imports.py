import os
import re

MODULES = [
    "context_tracker.py",
    "meta_ticker.py",
    "performance_monitor.py",
    "track_u_curiosity.py",
    "volition_seed.py",
    "weekly_summary.py",
]

# Assume this script is run from QPF Archive/Q 2.0/symbolic_modules/
all_py = set(f[:-3] for f in os.listdir('.') if f.endswith('.py'))

for fname in MODULES:
    if not os.path.exists(fname):
        print(f"⚠️ Skipping missing {fname}")
        continue

    with open(fname, "r", encoding="utf-8") as f:
        lines = f.readlines()

    changed = False
    new_lines = []
    for line in lines:
        # Only change 'from xyz import ...' where xyz is in all_py and not already relative
        m = re.match(r"\s*from (\w+) import (.+)", line)
        if m:
            mod = m.group(1)
            if mod in all_py and not line.strip().startswith("from ."):
                new_line = line.replace(f"from {mod} import", f"from .{mod} import")
                new_lines.append(new_line)
                changed = True
                continue
        new_lines.append(line)

    if changed:
        with open(fname, "w", encoding="utf-8") as f:
            f.writelines(new_lines)
        print(f"✅ Patched: {fname}")
    else:
        print(f"⏭️  No changes needed: {fname}")
