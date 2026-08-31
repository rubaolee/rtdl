#!/usr/bin/env python3
"""Create one exact Goal5817 execution authority after target preparation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from experiments.goal5817_three_arm.protocol import (
    build_authority, validate_authority,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument("--direct-binary", type=Path, required=True)
    parser.add_argument("--owner-directive", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.absolute()
    if output.exists():
        raise RuntimeError("Goal5817 authority output already exists")
    value = build_authority(
        args.freeze.resolve(strict=True),
        args.target_manifest.resolve(strict=True),
        args.direct_binary.resolve(strict=True),
        owner_directive=args.owner_directive,
    )
    validate_authority(
        value, freeze_path=args.freeze, target_manifest_path=args.target_manifest,
        direct_binary_path=args.direct_binary)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(
        json.dumps(value, indent=2, allow_nan=False, sort_keys=True).encode("utf-8")
        + b"\n")
    print(json.dumps({
        "status": value["status"],
        "authority_sha256": value["authority_sha256"],
        "formal_worker_count": 0,
        "registered_performance_timing_count": 0,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
