"""One fresh-process RTDL or PyOptiX worker for Goal5805."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import statistics
import time
from typing import Any

from .protocol import (
    ARMS, STEADY_REPETITIONS, STEADY_WARMUPS, file_record,
    validate_authority, validate_freeze, validate_runtime_manifest,
    validate_target_manifest,
)
from experiments.goal5802_premeasurement.workload import (
    RELATION_TASK, TRIANGLE_TASK, relation_workload, triangle_workload,
)


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Goal5805 JSON root differs: {path}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument("--authority", type=Path, required=True)
    parser.add_argument("--arm", choices=ARMS, required=True)
    parser.add_argument("--task", choices=("relation", "triangle"), required=True)
    parser.add_argument("--worker-id", required=True)
    args = parser.parse_args()

    root = args.root.resolve(strict=True)
    freeze_path = args.freeze.resolve(strict=True)
    target_path = args.target_manifest.resolve(strict=True)
    authority_path = args.authority.resolve(strict=True)
    freeze = _read(freeze_path)
    target = _read(target_path)
    authority = _read(authority_path)
    validate_freeze(freeze, root, rehash=True)
    validate_target_manifest(target, rehash=True)
    validate_authority(
        authority, freeze_file_sha256=_sha(freeze_path),
        target_manifest_file_sha256=_sha(target_path))
    files = target["files"]
    runtime_manifest = _read(Path(files["runtime_manifest"]["path"]))
    validate_runtime_manifest(runtime_manifest, rehash=True)
    runtime_target = runtime_manifest["target_observation"]
    if runtime_target.get("sha256") != files["target_observation"]["sha256"]:
        raise RuntimeError("Goal5805 target observation/runtime binding differs")
    task = RELATION_TASK if args.task == "relation" else TRIANGLE_TASK
    workload = relation_workload() if args.task == "relation" else triangle_workload()

    if args.arm == "RTDL":
        from experiments.goal5802_premeasurement.rtdlexe_arm import (
            RTDLDeploymentPaths, RTDLExecutableAdapter, preload_rtdl_runtime,
        )
        candidate_manifest = _read(Path(files["candidate_manifest"]["path"]))
        candidate = candidate_manifest["candidates"][args.task]
        runtime, implementation, preload = preload_rtdl_runtime()
        adapter = RTDLExecutableAdapter(
            task, workload,
            RTDLDeploymentPaths(
                artifact=Path(candidate["artifact_path"]),
                authority=Path(candidate["authority_path"]),
                trust_root=Path(files["trust_root"]["path"]),
                trust_head=Path(files["trust_head"]["path"]),
                trust_package=Path(files["trust_package"]["path"]),
                native_library=Path(files["native_library"]["path"]),
                deployment_id=candidate["deployment_id"],
            ),
            preloaded_runtime=runtime,
            preloaded_implementation=implementation,
            runtime_preload_receipt=preload,
        )
    else:
        from experiments.goal5802_premeasurement.pyoptix_scalar_arm import (
            PyOptixScalarAdapter, preload_pyoptix_runtime,
        )
        runtime, preload = preload_pyoptix_runtime()
        adapter = PyOptixScalarAdapter(
            task, workload,
            ptx_path=Path(files["matched_ptx"]["path"]),
            compaction_cubin_path=(
                Path(files["relation_compaction_cubin"]["path"])
                if args.task == "relation" else None),
            preloaded_runtime=runtime,
            runtime_preload_receipt=preload,
        )

    load_start = time.perf_counter_ns()
    adapter.load()
    load_end = time.perf_counter_ns()
    adapter.prepare()
    prepare_end = time.perf_counter_ns()
    execute = adapter.measurement_execution_callable()
    first_result = execute()
    first_end = time.perf_counter_ns()
    first_lifecycle = adapter.measurement_lifecycle_receipt(first_result)

    for _ in range(STEADY_WARMUPS):
        warm = execute()
        adapter.measurement_lifecycle_receipt(warm)
    steady_ns: list[int] = []
    last_result = first_result
    for _ in range(STEADY_REPETITIONS):
        start = time.perf_counter_ns()
        current = execute()
        end = time.perf_counter_ns()
        adapter.measurement_lifecycle_receipt(current)
        steady_ns.append(end - start)
        last_result = current
    evidence = adapter.finalize_measurement_evidence(last_result)
    adapter.close()
    result = {
        "schema": "rtdl.goal5805.formal_worker_result.v1",
        "status": "PASS",
        "worker_id": args.worker_id,
        "pid": os.getpid(),
        "arm": args.arm,
        "task": args.task,
        "freeze_file": file_record(freeze_path),
        "target_manifest_file": file_record(target_path),
        "authority_file": file_record(authority_path),
        "load_ns": load_end - load_start,
        "prepare_ns": prepare_end - load_end,
        "first_execute_ns": first_end - prepare_end,
        "deployment_cold_ns": first_end - load_start,
        "steady_ns": steady_ns,
        "steady_median_ns": int(statistics.median(steady_ns)),
        "first_lifecycle": first_lifecycle,
        "final_evidence": evidence,
        "registered_performance_timing_count": 2 + len(steady_ns),
        "formal_worker_count": 1,
    }
    print(json.dumps(result, allow_nan=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
