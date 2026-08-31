#!/usr/bin/env python3
"""Create the Goal5817 zero-worker scientific freeze."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from experiments.goal5817_three_arm.protocol import build_freeze, validate_freeze


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = args.root.resolve(strict=True)
    output = args.output.absolute()
    if output.exists():
        raise RuntimeError("Goal5817 freeze output already exists")
    value = build_freeze(root)
    validate_freeze(value, rehash=True, root=root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(
        json.dumps(value, indent=2, allow_nan=False, sort_keys=True).encode("utf-8")
        + b"\n")
    print(json.dumps({
        "status": value["status"],
        "freeze_sha256": value["freeze_sha256"],
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
