#!/usr/bin/env python3
"""Create-only Goal5798 runtime successor after the OptiX-8 header fix."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "experiments/goal5798_premeasurement/runtime_manifest_v6.json"
OUTPUT = ROOT / "experiments/goal5798_premeasurement/runtime_manifest_v7.json"


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
    for old in predecessor["files"]:
        path = ROOT / old["path"]
        rows.append({
            "bytes": path.stat().st_size,
            "path": old["path"],
            "sha256": sha(path),
        })
    changed = [
        row["path"] for row, old in zip(rows, predecessor["files"], strict=True)
        if row["bytes"] != old["bytes"] or row["sha256"] != old["sha256"]
    ]
    if changed != ["experiments/goal5798_premeasurement/build_direct_measurement.sh"]:
        raise RuntimeError(f"unexpected runtime successor delta: {changed}")
    result = {
        "schema": predecessor["schema"],
        "status": "EXACT_LOCAL_RUNTIME__EXECUTION_NOT_AUTHORIZED",
        "base_freeze_sha256": predecessor["base_freeze_sha256"],
        "base_source_manifest_sha256": predecessor["base_source_manifest_sha256"],
        "predecessor_manifest_file_sha256": sha(PREDECESSOR),
        "predecessor_manifest_sha256": predecessor["manifest_sha256"],
        "successor_reason": (
            "Treat the external OptiX include directory as a system include so "
            "OptiX 8.0 and older optix_stubs.h warnings do not become project -Werror failures."),
        "changed_path_count": 1,
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
