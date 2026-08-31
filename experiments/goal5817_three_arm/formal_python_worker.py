"""One fresh-process RTDL or PyOptiX metric worker for Goal5817."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import statistics
import time
from typing import Any

from experiments.goal5802_premeasurement.workload import (
    RELATION_TASK, TRIANGLE_TASK, relation_workload, triangle_workload,
)
from experiments.goal5805_successor.protocol import validate_target_manifest

from .protocol import (
    REGIMES, STEADY_REPETITIONS, STEADY_WARMUPS, TASKS, validate_freeze,
)


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"Goal5817 JSON root differs: {path}")
    return value


def _adapter(arm: str, task_name: str, target: dict[str, Any]):
    files = target["files"]
    task = RELATION_TASK if task_name == "relation" else TRIANGLE_TASK
    workload = relation_workload() if task_name == "relation" else triangle_workload()
    if arm == "RTDL":
        from experiments.goal5802_premeasurement.rtdlexe_arm import (
            RTDLDeploymentPaths, RTDLExecutableAdapter, preload_rtdl_runtime,
        )
        candidate_manifest = _read(Path(files["candidate_manifest"]["path"]))
        candidate = candidate_manifest["candidates"][task_name]
        runtime, implementation, preload = preload_rtdl_runtime()
        return RTDLExecutableAdapter(
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
    if arm != "PYOPTIX":
        raise RuntimeError(f"Goal5817 Python arm differs: {arm}")
    from experiments.goal5802_premeasurement.pyoptix_scalar_arm import (
        PyOptixScalarAdapter, preload_pyoptix_runtime,
    )
    runtime, preload = preload_pyoptix_runtime()
    return PyOptixScalarAdapter(
        task, workload,
        ptx_path=Path(files["matched_ptx"]["path"]),
        compaction_cubin_path=(
            Path(files["relation_compaction_cubin"]["path"])
            if task_name == "relation" else None),
        preloaded_runtime=runtime,
        runtime_preload_receipt=preload,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--freeze", type=Path, required=True)
    parser.add_argument("--target-manifest", type=Path, required=True)
    parser.add_argument("--authority-sha256", required=True)
    parser.add_argument("--arm", choices=("PYOPTIX", "RTDL"), required=True)
    parser.add_argument("--task", choices=TASKS, required=True)
    parser.add_argument("--regime", choices=REGIMES, required=True)
    parser.add_argument("--worker-id", required=True)
    args = parser.parse_args()
    if len(args.authority_sha256) != 64:
        raise RuntimeError("Goal5817 execution authority identity differs")
    root = args.root.resolve(strict=True)
    freeze = _read(args.freeze.resolve(strict=True))
    target = _read(args.target_manifest.resolve(strict=True))
    validate_freeze(freeze, rehash=False)
    validate_target_manifest(target, rehash=True)
    adapter = _adapter(args.arm, args.task, target)
    durations: list[int] = []
    lifecycle_receipts: list[dict[str, Any]] = []
    last_result = None

    if args.regime == "DEPLOYMENT_COLD":
        start = time.perf_counter_ns()
        adapter.load()
        adapter.prepare()
        execute = adapter.measurement_execution_callable()
        last_result = execute()
        durations.append(time.perf_counter_ns() - start)
        lifecycle_receipts.append(adapter.measurement_lifecycle_receipt(last_result))
    elif args.regime == "PREPARE":
        adapter.load()
        start = time.perf_counter_ns()
        adapter.prepare()
        durations.append(time.perf_counter_ns() - start)
        execute = adapter.measurement_execution_callable()
        last_result = execute()
        lifecycle_receipts.append(adapter.measurement_lifecycle_receipt(last_result))
    else:
        adapter.load()
        adapter.prepare()
        execute = adapter.measurement_execution_callable()
        for _ in range(STEADY_WARMUPS):
            warm = execute()
            adapter.measurement_lifecycle_receipt(warm)
        for _ in range(STEADY_REPETITIONS):
            start = time.perf_counter_ns()
            current = execute()
            end = time.perf_counter_ns()
            lifecycle_receipts.append(
                adapter.measurement_lifecycle_receipt(current))
            durations.append(end - start)
            last_result = current

    if last_result is None:
        raise RuntimeError("Goal5817 Python arm produced no exact result")
    evidence = adapter.finalize_measurement_evidence(last_result)
    adapter.close()
    metric = int(statistics.median(durations))
    result = {
        "schema": "rtdl.goal5817.python_metric_worker.v1",
        "status": "PASS",
        "worker_id": args.worker_id,
        "pid": os.getpid(),
        "arm": args.arm,
        "task": args.task,
        "regime": args.regime,
        "metric_ns": metric,
        "durations_ns": durations,
        "steady_warmups": STEADY_WARMUPS if args.regime == "STEADY_E2E" else 0,
        "lifecycle_receipt_count": len(lifecycle_receipts),
        "final_evidence": evidence,
        "registered_performance_timing_count": len(durations),
        "formal_worker_count": 1,
        "receipt_serialization_inside_timer": False,
        "close_inside_timer": False,
        "runtime_import_inside_timer": False,
    }
    print(json.dumps(result, allow_nan=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
