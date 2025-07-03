import os
import sys

docs = [
    "docs/README.md",
    "docs/FEATURES.md",
    "docs/PLAN.md",
    "docs/TASKS.md",
]

missing = [d for d in docs if not os.path.exists(d)]
empty = [d for d in docs if os.path.exists(d) and os.path.getsize(d) == 0]

if missing or empty:
    if missing:
        print("Missing files:", ", ".join(missing))
    if empty:
        print("Empty files:", ", ".join(empty))
    sys.exit(1)

print("All documentation files exist and are non-empty.")
