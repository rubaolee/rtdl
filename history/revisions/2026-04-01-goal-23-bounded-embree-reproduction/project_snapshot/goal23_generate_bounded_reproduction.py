#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

from rtdsl.goal23_reproduction import generate_goal23_artifacts

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    artifacts = generate_goal23_artifacts(output_dir=ROOT / "build" / "goal23_reproduction")
    for key, path in artifacts.items():
        print(f"{key}: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
