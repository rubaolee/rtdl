#!/usr/bin/env python3
"""Rehash a Goal5802 load-bearing header projection without timing."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.goal5802_build_header_projection_untimed import (
    validate_header_projection,
    validate_projection_only,
    validate_provenance,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--projection-root", type=Path, required=True)
    parser.add_argument(
        "--mode", required=True,
        choices=("projection-only", "provenance-only", "full"))
    args = parser.parse_args()
    receipt = args.receipt.resolve(strict=True)
    value = json.loads(receipt.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError("header projection receipt is not an object")
    if args.mode == "projection-only":
        validate_projection_only(value, args.projection_root)
    elif args.mode == "provenance-only":
        validate_provenance(value, args.projection_root)
    else:
        validate_header_projection(value, args.projection_root)
    print(json.dumps({
        "status": "PASS__UNTIMED_HEADER_PROJECTION_REHASH",
        "receipt_sha256": value["receipt_sha256"],
        "projection_tree_sha256": value["projection_tree_sha256"],
        "projection_file_count": value["projection_file_count"],
        "verification_mode": args.mode,
        "registered_performance_timing_count": 0,
        "gpu_kernel_launch_count": 0,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
