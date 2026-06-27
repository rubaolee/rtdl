from __future__ import annotations

from pathlib import Path
import runpy
import sys


ROOT = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
TARGET = ROOT / "examples" / "benchmark_apps" / "spatial_rayjoin" / "rtdl_rayjoin_v2_spatial_join_app.py"


def main() -> int:
    sys.argv[0] = str(TARGET)
    runpy.run_path(str(TARGET), run_name="__main__")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
