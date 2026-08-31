#!/usr/bin/env python3
"""Create an exact, owner-directed Goal5805 formal execution authority."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from experiments.goal5805_successor.protocol import (
    AUTHORITY_SCHEMA, digest, validate_authority,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--owner-directive", required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise RuntimeError("Goal5805 authority output already exists")
    freeze = args.freeze.resolve(strict=True)
    target = args.target_manifest.resolve(strict=True)
    if not args.owner_directive.strip():
        raise RuntimeError("Goal5805 owner directive is empty")
    value = {
        "schema": AUTHORITY_SCHEMA,
        "freeze_file_sha256": _sha(freeze),
        "target_manifest_file_sha256": _sha(target),
        "owner_directive": args.owner_directive,
        "owner_execution_authorized": True,
        "formal_worker_zero_authorized": True,
        "pod_gpu_timing_authorized": True,
        "unconditional_result_acceptance": True,
        "retry_replacement_row_drop": False,
    }
    value["authority_sha256"] = digest(value)
    validate_authority(
        value, freeze_file_sha256=_sha(freeze),
        target_manifest_file_sha256=_sha(target))
    args.output.write_bytes(json.dumps(
        value, indent=2, allow_nan=False, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({"authority_sha256": value["authority_sha256"]},
                     sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

