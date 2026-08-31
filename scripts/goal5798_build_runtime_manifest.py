#!/usr/bin/env python3
"""Build the exact Goal5798 runtime manifest from the controlling freeze."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
GOAL = ROOT / "experiments" / "goal5798_premeasurement"
if str(GOAL) not in sys.path:
    sys.path.insert(0, str(GOAL))
from contract_runtime import digest, load_freeze


NEW_RUNTIME_FILES = (
    "experiments/goal5798_premeasurement/build_direct_measurement.sh",
    "experiments/goal5798_premeasurement/controller.py",
    "experiments/goal5798_premeasurement/direct_measurement.cpp",
    "experiments/goal5798_premeasurement/formal_contract_runtime.py",
    "experiments/goal5798_premeasurement/pyoptix_worker.py",
    "experiments/goal5798_premeasurement/rtdl_worker.py",
    "experiments/goal5798_premeasurement/worker_common.py",
    "src/native/rtdl_optix.cpp",
)


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    freeze = load_freeze(args.freeze.resolve())
    rows = {row["path"]: dict(row) for row in freeze["source_manifest"]}
    for relative, row in rows.items():
        path = ROOT / relative
        if not path.is_file() or path.stat().st_size != row["bytes"] or sha(path) != row["sha256"]:
            raise RuntimeError(f"controlling-freeze source drift: {relative}")
    for relative in NEW_RUNTIME_FILES:
        path = ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(path)
        rows[relative] = {
            "path": relative, "bytes": path.stat().st_size, "sha256": sha(path),
        }
    files = [rows[key] for key in sorted(rows)]
    result = {
        "schema": "rtdl.goal5798.runtime_manifest.v1",
        "status": "EXACT_LOCAL_RUNTIME__EXECUTION_NOT_AUTHORIZED",
        "base_freeze_sha256": freeze["freeze_sha256"],
        "base_source_manifest_sha256": freeze["source_manifest_sha256"],
        "file_count": len(files),
        "total_bytes": sum(row["bytes"] for row in files),
        "files": files,
    }
    result["manifest_sha256"] = digest(result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(json.dumps(
        result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": "PASS", "output": str(args.output),
        "manifest_sha256": result["manifest_sha256"], "file_count": len(files),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
