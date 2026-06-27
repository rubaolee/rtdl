from __future__ import annotations

from pathlib import Path
import runpy
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
TARGET = ROOT / "examples" / "benchmark_apps" / "barnes_hut" / "rtdl_barnes_hut_benchmark_app.py"


def main() -> int:
    sys.argv[0] = str(TARGET)
    runpy.run_path(str(TARGET), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
