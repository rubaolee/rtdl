from __future__ import annotations

from pathlib import Path
import sys


def ensure_repo_src_on_path() -> None:
    root = next(parent for parent in Path(__file__).resolve().parents if (parent / "src" / "rtdsl").exists())
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
