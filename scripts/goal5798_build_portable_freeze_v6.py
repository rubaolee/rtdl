#!/usr/bin/env python3
"""Create-only Goal5798 freeze successor for the OptiX-7.6 API shim."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
GOAL = ROOT / "experiments/goal5798_premeasurement"
sys.path.insert(0, str(GOAL))
from contract_runtime import digest, validate_freeze


PREDECESSOR = ROOT / "history/internal_docs/goal5798_a1_portable_premeasurement_freeze_v5_20260823.json"
OUTPUT = ROOT / "history/internal_docs/goal5798_a2_optix76_compatible_premeasurement_freeze_v6_20260823.json"
EXPECTED_CHANGED = [
    "experiments/goal5796_matched/direct_optix.cpp",
    "src/native/optix/rtdl_optix_core.cpp",
    "src/native/optix/rtdl_optix_prelude.h",
    "src/native/optix/rtdl_optix_v4_callback_poc.cpp",
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    if OUTPUT.exists():
        raise FileExistsError(OUTPUT)
    predecessor = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    manifest = []
    changed = []
    for old in predecessor["source_manifest"]:
        path = ROOT / old["path"]
        row = {"path": old["path"], "bytes": path.stat().st_size, "sha256": sha(path)}
        manifest.append(row)
        if row["bytes"] != old["bytes"] or row["sha256"] != old["sha256"]:
            changed.append(row["path"])
    if changed != EXPECTED_CHANGED:
        raise RuntimeError(f"unexpected scientific-source delta: {changed}")
    result = json.loads(json.dumps(predecessor))
    result.pop("freeze_sha256")
    result["status"] = "OPTIX_7_6_COMPATIBLE_SUCCESSOR_FROZEN__EXECUTION_FORBIDDEN"
    result["supersedes_portable_freeze"] = {
        "path": PREDECESSOR.relative_to(ROOT).as_posix(),
        "bytes": PREDECESSOR.stat().st_size,
        "file_sha256": sha(PREDECESSOR),
        "freeze_sha256": predecessor["freeze_sha256"],
    }
    result["compatibility_amendment"] = {
        "changed_paths": changed,
        "runtime_semantics_on_optix_7_7_and_newer": "UNCHANGED_BY_PREPROCESSOR_BRANCH",
        "optix_7_6_module_entry": "optixModuleCreateFromPTX",
        "optix_7_7_and_newer_module_entry": "optixModuleCreate",
        "optix_7_6_stack_accumulator_arity": 2,
        "optix_7_7_and_newer_stack_accumulator_arity": 3,
        "task_schedule_changed": False,
        "statistics_changed": False,
        "workload_changed": False,
        "prior_performance_result_relabelled": False,
        "authorization": False,
    }
    result["source_manifest"] = manifest
    result["source_manifest_file_count"] = len(manifest)
    result["source_manifest_sha256"] = digest(manifest)
    result["implementation_status"]["physical_host_binding"] = "ABSENT"
    result["implementation_status"]["worker_zero_ready"] = False
    result["registered_performance_timing_count"] = 0
    result["gpu_execution_count"] = 0
    result["freeze_sha256"] = digest(result)
    validate_freeze(result)
    OUTPUT.write_bytes(json.dumps(result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps({
        "status": "PASS", "file_sha256": sha(OUTPUT),
        "freeze_sha256": result["freeze_sha256"],
        "changed_paths": changed,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
