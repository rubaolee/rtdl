#!/usr/bin/env python3
"""Create-only runtime manifest for the portable performance successor."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "experiments/goal5798_premeasurement/runtime_manifest_v8.json"
OUTPUT = ROOT / "experiments/goal5798_premeasurement/runtime_manifest_v9.json"
EXPECTED_CHANGED = [
    "src/native/optix/rtdl_optix_api.cpp",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
    "src/rtdsl/__init__.py",
    "src/rtdsl/_v4_numba_compile_child.py",
    "src/rtdsl/v4_bounded_relation.py",
    "src/rtdsl/v4_bounded_relation_optix_compiler.py",
    "src/rtdsl/v4_bounded_relation_optix_wrapper_codegen.py",
    "src/rtdsl/v4_bounded_relation_prepared_runtime.py",
    "src/rtdsl/v4_box_relation_callback.py",
    "src/rtdsl/v4_callback_lifecycle.py",
    "src/rtdsl/v4_callback_numba_codegen.py",
    "src/rtdsl/v4_callback_ptx_composer.py",
    "src/rtdsl/v4_triangle_reduction_optix_compiler.py",
    "src/rtdsl/v4_triangle_reduction_optix_runtime.py",
    "src/rtdsl/v4_triangle_reduction_prepared_runtime.py",
]


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode("utf-8")).hexdigest()


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    predecessor = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    rows = []
    changed = []
    for old in predecessor["files"]:
        path = ROOT / old["path"]
        row = {
            "bytes": path.stat().st_size,
            "path": old["path"],
            "sha256": sha(path),
        }
        rows.append(row)
        if row["bytes"] != old["bytes"] or row["sha256"] != old["sha256"]:
            changed.append(row["path"])
    if changed != EXPECTED_CHANGED:
        raise RuntimeError(f"unexpected runtime successor delta: {changed}")
    result = {
        "schema": predecessor["schema"],
        "status": "EXACT_LOCAL_RUNTIME__EXECUTION_NOT_AUTHORIZED",
        "base_freeze_sha256": predecessor["base_freeze_sha256"],
        "base_source_manifest_sha256": predecessor["base_source_manifest_sha256"],
        "predecessor_manifest_file_sha256": sha(PREDECESSOR),
        "predecessor_manifest_sha256": predecessor["manifest_sha256"],
        "successor_reason": (
            "Remove repeated public-lifecycle work while preserving exact "
            "Callback-IR, status, output, and target/toolchain identities; "
            "make historical package exports lazy so the narrow V4 entrypoint "
            "does not import unrelated subsystems."
        ),
        "changed_path_count": len(changed),
        "changed_paths": changed,
        "file_count": len(rows),
        "total_bytes": sum(row["bytes"] for row in rows),
        "files": rows,
    }
    result["manifest_sha256"] = canonical_digest(result)
    OUTPUT.write_bytes(
        json.dumps(result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": "PASS",
        "file_count": len(rows),
        "file_sha256": sha(OUTPUT),
        "manifest_sha256": result["manifest_sha256"],
        "changed_paths": changed,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
