#!/usr/bin/env python3
"""Create-only runtime manifest for the OptiX-7.6 source successor."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "experiments/goal5798_premeasurement/runtime_manifest_v7.json"
FREEZE = ROOT / "history/internal_docs/goal5798_a2_optix76_compatible_premeasurement_freeze_v6_20260823.json"
OUTPUT = ROOT / "experiments/goal5798_premeasurement/runtime_manifest_v8.json"
EXPECTED_CHANGED = [
    "experiments/goal5796_matched/direct_optix.cpp",
    "src/native/optix/rtdl_optix_core.cpp",
    "src/native/optix/rtdl_optix_prelude.h",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
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
    freeze = json.loads(FREEZE.read_text(encoding="utf-8"))
    rows = []
    changed = []
    for old in predecessor["files"]:
        path = ROOT / old["path"]
        row = {"bytes": path.stat().st_size, "path": old["path"], "sha256": sha(path)}
        rows.append(row)
        if row["bytes"] != old["bytes"] or row["sha256"] != old["sha256"]:
            changed.append(row["path"])
    if changed != EXPECTED_CHANGED:
        raise RuntimeError(f"unexpected runtime successor delta: {changed}")
    result = {
        "schema": predecessor["schema"],
        "status": "EXACT_LOCAL_RUNTIME__EXECUTION_NOT_AUTHORIZED",
        "base_freeze_sha256": freeze["freeze_sha256"],
        "base_source_manifest_sha256": freeze["source_manifest_sha256"],
        "predecessor_manifest_file_sha256": sha(PREDECESSOR),
        "predecessor_manifest_sha256": predecessor["manifest_sha256"],
        "successor_reason": "Compile-time OptiX-7.6/7.7 API compatibility shims.",
        "changed_path_count": len(changed),
        "changed_paths": changed,
        "file_count": len(rows),
        "total_bytes": sum(row["bytes"] for row in rows),
        "files": rows,
    }
    result["manifest_sha256"] = canonical_digest(result)
    OUTPUT.write_bytes(json.dumps(result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": "PASS", "file_count": len(rows),
        "file_sha256": sha(OUTPUT),
        "manifest_sha256": result["manifest_sha256"],
        "changed_paths": changed,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
