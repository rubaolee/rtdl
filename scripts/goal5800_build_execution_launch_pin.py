#!/usr/bin/env python3
"""Freeze a separate pre-run trust anchor for a Goal5800 source authority."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


HEX40 = re.compile(r"[0-9a-f]{40}")
HEX64 = re.compile(r"[0-9a-f]{64}")


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def build(authority_path: Path) -> dict[str, object]:
    resolved = authority_path.resolve(strict=True)
    raw = resolved.read_bytes()
    authority = json.loads(raw)
    if (type(authority) is not dict
            or authority.get("schema")
            != "rtdl.goal5800.pyoptix_execution_authority.v2"
            or authority.get("status") != "FROZEN__PREEXECUTION_SOURCE_AUTHORITY"
            or authority.get("capture_phase")
            != "BEFORE_PYOPTIX_CUPY_IMPORT_OR_CUDA_OPTIX_INITIALIZATION"
            or authority.get("registered_performance_timing_count") != 0
            or authority.get("git_membership_proof", {}).get(
                "all_required_files_exact_origin_blobs") is not True
            or HEX40.fullmatch(str(authority.get("origin_repository_commit"))) is None
            or HEX40.fullmatch(str(authority.get("origin_repository_tree"))) is None
            or HEX64.fullmatch(sha256(raw)) is None):
        raise RuntimeError("execution authority is not v2 Git-membership closeable")
    return {
        "schema": "rtdl.goal5800.pyoptix_execution_launch_pin.v1",
        "status": "FROZEN__SEPARATE_PREEXECUTION_TRUST_ANCHOR",
        "capture_phase": "AFTER_AUTHORITY_FREEZE__BEFORE_PYOPTIX_CUPY_IMPORT_OR_GPU_EXECUTION",
        "authority": {
            "path": str(resolved), "bytes": len(raw), "sha256": sha256(raw),
        },
        "authority_schema": authority["schema"],
        "origin_repository_commit": authority["origin_repository_commit"],
        "origin_repository_tree": authority["origin_repository_tree"],
        "executed_source_file_count": authority["file_count"],
        "all_required_files_exact_origin_blobs": True,
        "changed_expected_allowed": False,
        "registered_performance_timing_count": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    document = build(args.authority)
    value = json.dumps(document, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(value)
    print(json.dumps({
        "status": document["status"], "output": str(args.output),
        "bytes": len(value), "sha256": sha256(value),
        "registered_performance_timing_count": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
