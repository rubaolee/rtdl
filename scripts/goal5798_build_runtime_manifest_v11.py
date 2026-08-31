#!/usr/bin/env python3
"""Freeze the Goal5798 immutable-input-reuse runtime successor."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "experiments/goal5798_premeasurement/runtime_manifest_v10.json"
OUTPUT = ROOT / "experiments/goal5798_premeasurement/runtime_manifest_v11.json"
CHANGED_PATHS = (
    "src/native/optix/rtdl_optix_api.cpp",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
    "src/rtdsl/v4_bounded_relation_prepared_runtime.py",
    "src/rtdsl/v4_triangle_reduction_prepared_runtime.py",
)


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
    allowed = set(CHANGED_PATHS)
    observed_changed: list[str] = []
    rows: list[dict[str, object]] = []
    for old in predecessor["files"]:
        path = ROOT / old["path"]
        row = {
            "bytes": path.stat().st_size,
            "path": old["path"],
            "sha256": sha(path),
        }
        rows.append(row)
        changed = row["bytes"] != old["bytes"] or row["sha256"] != old["sha256"]
        if changed:
            observed_changed.append(str(old["path"]))
    if set(observed_changed) != allowed:
        raise RuntimeError(
            f"runtime delta differs from exact successor scope: {observed_changed}")
    result = {
        "schema": predecessor["schema"],
        "status": "EXACT_LOCAL_RUNTIME__EXECUTION_NOT_AUTHORIZED",
        "base_freeze_sha256": predecessor["base_freeze_sha256"],
        "base_source_manifest_sha256": predecessor["base_source_manifest_sha256"],
        "predecessor_manifest_file_sha256": sha(PREDECESSOR),
        "predecessor_manifest_sha256": predecessor["manifest_sha256"],
        "successor_reason": (
            "Make the public prepared lifecycle retain exact immutable query "
            "inputs on the device. Conservative v1/v2 native ABIs remain "
            "unchanged; new reuse ABIs reject calls without an exact uploaded "
            "predecessor, and Python cache identities publish only after success."
        ),
        "outcome_directed_after_predecessor_formal_loss": True,
        "predecessor_formal_result_replaced": False,
        "generalization_exam_claimed": False,
        "changed_path_count": len(observed_changed),
        "changed_paths": sorted(observed_changed),
        "added_path_count": 0,
        "added_paths": [],
        "file_count": len(rows),
        "total_bytes": sum(int(row["bytes"]) for row in rows),
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
        "changed_paths": sorted(observed_changed),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
