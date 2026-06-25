from __future__ import annotations

from pathlib import Path
import runpy
import sys


def run(example_name: str) -> int:
    root = Path(__file__).resolve().parents[2]
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    target = root / "future" / "v4" / "examples" / example_name
    sys.argv[0] = str(target)
    runpy.run_path(str(target), run_name="__main__")
    return 0
