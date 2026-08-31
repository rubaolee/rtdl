#!/usr/bin/env python3
"""Build the create-only Goal5805 pre-formal protocol freeze."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from experiments.goal5805_successor.protocol import build_freeze, validate_freeze


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--predecessor-result-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise RuntimeError("Goal5805 freeze output already exists")
    value = build_freeze(
        args.root, predecessor_result_sha256=args.predecessor_result_sha256)
    validate_freeze(value, args.root, rehash=True)
    args.output.write_bytes(json.dumps(
        value, indent=2, allow_nan=False, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({"freeze_sha256": value["freeze_sha256"],
                      "formal_worker_count": 0,
                      "registered_performance_timing_count": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

