#!/usr/bin/env python3
"""Bind a completed build-only compatibility matrix to an exact runtime tree.

This is deliberately a post-run custody record.  It does not relabel an old
result field or claim that an ABI import is an application execution.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import time


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")).hexdigest()


def create_json(path: Path, value: dict[str, object]) -> None:
    if path.exists():
        raise FileExistsError(path)
    temporary = path.with_name(f".{path.name}.tmp.{os.getpid()}.{time.monotonic_ns()}")
    payload = json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    descriptor = os.open(temporary, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb", closefd=False) as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.link(temporary, path)
    finally:
        os.close(descriptor)
        temporary.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--matrix-result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    source_root = args.source_root.resolve()
    manifest_path = args.manifest.resolve()
    matrix_path = args.matrix_result.resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    matrix = json.loads(matrix_path.read_text(encoding="utf-8"))

    manifest_unsigned = dict(manifest)
    claimed_manifest_sha = manifest_unsigned.pop("manifest_sha256")
    if canonical_digest(manifest_unsigned) != claimed_manifest_sha:
        raise RuntimeError("runtime manifest seal mismatch")
    matrix_unsigned = dict(matrix)
    claimed_matrix_sha = matrix_unsigned.pop("result_sha256")
    if canonical_digest(matrix_unsigned) != claimed_matrix_sha:
        raise RuntimeError("compatibility result seal mismatch")
    if matrix.get("status") != "PASS" or matrix.get("stack_count") != 6:
        raise RuntimeError("compatibility matrix is not a six-row PASS")

    mismatches: list[dict[str, object]] = []
    for row in manifest["files"]:
        path = source_root / row["path"]
        actual_bytes = path.stat().st_size if path.is_file() else None
        actual_sha = sha256(path) if path.is_file() else None
        if actual_bytes != row["bytes"] or actual_sha != row["sha256"]:
            mismatches.append({
                "path": row["path"],
                "expected_bytes": row["bytes"],
                "actual_bytes": actual_bytes,
                "expected_sha256": row["sha256"],
                "actual_sha256": actual_sha,
            })
    if mismatches:
        raise RuntimeError(f"runtime tree mismatch: {mismatches[:3]}")

    old_label = (
        "experiments/goal5798_premeasurement/runtime_manifest_v8.json"
        in matrix.get("source_inputs", {})
    )
    result: dict[str, object] = {
        "schema": "rtdl.goal5798.compatibility_runtime_postrun_binding.v2",
        "status": "PASS__POSTRUN_SOURCE_CUSTODY_ONLY",
        "matrix_result_file_sha256": sha256(matrix_path),
        "matrix_result_sha256": claimed_matrix_sha,
        "matrix_status": matrix["status"],
        "matrix_stack_count": matrix["stack_count"],
        "matrix_gpu_workload_executed": matrix["gpu_workload_executed"],
        "matrix_application_result_observed": matrix["application_result_observed"],
        "runtime_manifest_file_sha256": sha256(manifest_path),
        "runtime_manifest_sha256": claimed_manifest_sha,
        "runtime_file_count": manifest["file_count"],
        "runtime_rehash_mismatch_count": len(mismatches),
        "matrix_metadata_names_predecessor_manifest_v8": old_label,
        "predecessor_label_not_rewritten": True,
        "binding_interpretation": (
            f"The source tree rehashed exactly to {manifest_path.name} immediately "
            "after the completed build-only matrix.  This closes post-run source "
            "custody; it does not rewrite the matrix's v8 metadata label, prove "
            "runtime execution on six drivers, or create performance evidence."
        ),
    }
    result["binding_sha256"] = canonical_digest(result)
    create_json(args.output.resolve(), result)
    print(json.dumps({
        "status": result["status"],
        "binding_sha256": result["binding_sha256"],
        "runtime_rehash_mismatch_count": 0,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
