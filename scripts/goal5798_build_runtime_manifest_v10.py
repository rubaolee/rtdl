#!/usr/bin/env python3
"""Create-only completeness successor to Goal5798 runtime manifest v9."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "experiments/goal5798_premeasurement/runtime_manifest_v9.json"
OUTPUT = ROOT / "experiments/goal5798_premeasurement/runtime_manifest_v10.json"
ADDED_PATH = "src/rtdsl/v4_inline_cuda_codegen.py"


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
    rows: list[dict[str, object]] = []
    drift: list[str] = []
    for old in predecessor["files"]:
        path = ROOT / old["path"]
        row = {
            "bytes": path.stat().st_size,
            "path": old["path"],
            "sha256": sha(path),
        }
        rows.append(row)
        if row["bytes"] != old["bytes"] or row["sha256"] != old["sha256"]:
            drift.append(old["path"])
    if drift:
        raise RuntimeError(f"unexpected predecessor drift: {drift}")
    added = ROOT / ADDED_PATH
    if not added.is_file():
        raise FileNotFoundError(added)
    rows.append({
        "bytes": added.stat().st_size,
        "path": ADDED_PATH,
        "sha256": sha(added),
    })
    rows.sort(key=lambda row: str(row["path"]))
    result = {
        "schema": predecessor["schema"],
        "status": "EXACT_LOCAL_RUNTIME__EXECUTION_NOT_AUTHORIZED",
        "base_freeze_sha256": predecessor["base_freeze_sha256"],
        "base_source_manifest_sha256": predecessor["base_source_manifest_sha256"],
        "predecessor_manifest_file_sha256": sha(PREDECESSOR),
        "predecessor_manifest_sha256": predecessor["manifest_sha256"],
        "successor_reason": (
            "Close the clean-package dependency graph by adding the inline CUDA "
            "lowering module imported by v4_bounded_relation_optix_compiler."
        ),
        "changed_path_count": 0,
        "changed_paths": [],
        "added_path_count": 1,
        "added_paths": [ADDED_PATH],
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
        "added_paths": [ADDED_PATH],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
