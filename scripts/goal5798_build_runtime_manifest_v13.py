#!/usr/bin/env python3
"""Freeze the Goal5798 v12 baseline-symmetry runtime successor."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PREDECESSOR = ROOT / "experiments/goal5798_premeasurement/runtime_manifest_v12.json"
OUTPUT = ROOT / "experiments/goal5798_premeasurement/runtime_manifest_v13.json"
CHANGED_PATHS = (
    "experiments/goal5798_premeasurement/pyoptix_worker.py",
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
    rows: list[dict[str, object]] = []
    observed_changed: list[str] = []
    for old in predecessor["files"]:
        path = ROOT / old["path"]
        row = {
            "bytes": path.stat().st_size,
            "path": old["path"],
            "sha256": sha(path),
        }
        rows.append(row)
        if row["bytes"] != old["bytes"] or row["sha256"] != old["sha256"]:
            observed_changed.append(str(old["path"]))
    if set(observed_changed) != set(CHANGED_PATHS):
        raise RuntimeError(
            f"runtime delta differs from exact successor scope: {observed_changed}")
    result = {
        "schema": predecessor["schema"],
        "status": "EXACT_LOCAL_RUNTIME__EXTERNAL_PREEXECUTION_GATE_REQUIRED",
        "base_freeze_sha256": predecessor["base_freeze_sha256"],
        "base_source_manifest_sha256": predecessor["base_source_manifest_sha256"],
        "predecessor_manifest_file_sha256": sha(PREDECESSOR),
        "predecessor_manifest_sha256": predecessor["manifest_sha256"],
        "successor_reason": (
            "Remove RTDL's measured advantage by replacing only the PyOptiX "
            "arm's per-element NumPy scalar conversion with standard bulk "
            "tolist materialization; accept every result including 0/8."
        ),
        "outcome_directed_after_v11_favorable_result": True,
        "direction_of_change": "PYOPTIX_BASELINE_ONLY__CAN_ONLY_LOWER_RTDL_RATIOS",
        "predecessor_formal_result_replaced": False,
        "prepared_advantage_claim_withdrawn": True,
        "oracle_weakened": False,
        "device_status_or_output_download_removed": False,
        "formal_worker_count_authorized_before_external_gate": 0,
        "post_v12_successor_allowed": False,
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
