#!/usr/bin/env python3
"""Bind target-built products without executing a performance worker."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from experiments.goal5805_successor.protocol import (
    TARGET_SCHEMA, digest, file_record, validate_target_manifest,
)


def main() -> int:
    parser = argparse.ArgumentParser()
    for name in (
        "candidate-manifest", "trust-root", "trust-head", "trust-package",
        "native-library", "matched-ptx", "relation-compaction-cubin",
        "runtime-manifest", "target-observation"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise RuntimeError("Goal5805 target manifest output already exists")
    files = {
        name: file_record(getattr(args, name)) for name in (
            "candidate_manifest", "trust_root", "trust_head", "trust_package",
            "native_library", "matched_ptx", "relation_compaction_cubin",
            "runtime_manifest", "target_observation")
    }
    value = {
        "schema": TARGET_SCHEMA,
        "status": "TARGET_PRODUCTS_FROZEN__FORMAL_WORKER_ZERO",
        "files": files,
        "registered_performance_timing_count": 0,
        "formal_worker_count": 0,
    }
    value["target_manifest_sha256"] = digest(value)
    validate_target_manifest(value, rehash=True)
    args.output.write_bytes(json.dumps(
        value, indent=2, allow_nan=False, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({"target_manifest_sha256": value["target_manifest_sha256"],
                      "formal_worker_count": 0,
                      "registered_performance_timing_count": 0}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
