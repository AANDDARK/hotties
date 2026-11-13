import os
import time
from typing import Callable

IGNORED_DIRS = {".git", "node_modules", "__pycache__", ".venv", ".idea"}


def snapshot(root: str) -> dict[str, int]:
    snap: dict[str, int] = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORED_DIRS]
        for f in filenames:
            path = os.path.join(dirpath, f)
            try:
                snap[path] = os.stat(path).st_mtime_ns
            except OSError:
                pass  
    return snap


def watch(callback: Callable[[], object], root: str = ".", interval: float = 0.3) -> None:
    callback()
    prev = snapshot(root)
    print(f"\nWatching '{os.path.abspath(root)}' (Ctrl+C to stop)...")

    try:
        while True:
            time.sleep(interval)
            cur = snapshot(root)
            if cur != prev:
                print("\n--- change detected ---")
                callback()
                prev = snapshot(root) 
    except KeyboardInterrupt:
        print("\nStopped.")