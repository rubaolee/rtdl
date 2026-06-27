from __future__ import annotations

from pathlib import Path
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.benchmark_apps._support.v4_public_entry import main


if __name__ == "__main__":
    raise SystemExit(main("barnes_hut"))
