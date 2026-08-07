"""B3-1 Mini Redis CLI entry point."""

import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from mini_redis.cli import run_repl


if __name__ == "__main__":
    run_repl()
