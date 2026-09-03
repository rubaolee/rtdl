#!/usr/bin/env python3
"""Timer-free package-front-door witness for Goal5842's PyOptiX arm."""

from __future__ import annotations

import argparse
import gc
import hashlib
import importlib.metadata
import json
from pathlib import Path

from experiments.goal5842_causal_admission.contracts import (
    BASELINE_TASKS,
    PYOPTIX_IDENTITY_WITNESS_SCHEMA,
    RELATION_TASK,
    STEADY_REPETITIONS,
    STEADY_WARMUPS,
    TRIANGLE_TASK,
    digest,
)
from experiments.goal5842_causal_admission.runtime import (
    create_json,
    load_execution_authority,
    require_bound_path,
    require_idle_bound_gpu,
)
from experiments.goal5842_causal_admission.tasks import build_task

ROOT = Path(__file__).resolve().parents[1]


def verify_output(task_id: str, value: dict[str, object], expected: object) -> str:
    if task_id == RELATION_TASK:
        rows = tuple(tuple(int(item) for item in row) for row in value["output"])
        if rows != expected:
            raise RuntimeError("PyOptiX relation witness output mismatch")
        return digest(rows)
    if task_id == TRIANGLE_TASK:
        weighted = int(value["weighted_sum"])
        per_ray = tuple(int(item) for item in value["per_ray"])
        if weighted != expected["weighted_sum"] or per_ray != expected["per_ray"]:
            raise RuntimeError("PyOptiX triangle witness output mismatch")
        return digest(weighted)
    raise ValueError(f"unsupported PyOptiX witness task: {task_id}")


def execute_task(
    task_id: str,
    *,
    device_source: Path,
    ptx: bytes,
) -> dict[str, object]:
    from experiments.goal5796_matched import pyoptix_baseline as baseline
    from experiments.goal5798_premeasurement.pyoptix_worker import (
        PyOptixRelationPrepared,
        PyOptixTrianglePrepared,
    )

    print(
        json.dumps(
            {
                "schema": "rtdl.goal5842.pyoptix_identity_progress.v1",
                "task": task_id,
                "phase": "BEGIN_UNTIMED_EXECUTION",
            },
            sort_keys=True,
        ),
        flush=True,
    )
    task = build_task(task_id)
    raw = task.provider_fixture
    if not isinstance(raw, dict):
        raise TypeError("PyOptiX witness task lacks provider fixture")
    context, logger = baseline.make_context()
    task_name = "relation" if task_id == RELATION_TASK else "triangle"
    pipeline, groups, logs = baseline.build_pipeline(context, ptx, task=task_name)
    sbt, sbt_keepalive = baseline.make_sbt(groups)
    prepared = None
    try:
        if task_id == RELATION_TASK:
            prepared = PyOptixRelationPrepared(baseline, context, pipeline, sbt, raw)
        else:
            prepared = PyOptixTrianglePrepared(baseline, context, pipeline, sbt, raw)
        complete_execution_call_count = STEADY_WARMUPS + STEADY_REPETITIONS
        output_sha256 = ""
        for _ in range(complete_execution_call_count):
            output_sha256 = verify_output(
                task_id, prepared.execute(), task.expected_output
            )
    finally:
        del prepared, sbt, sbt_keepalive, groups, pipeline, context, logger, logs
        gc.collect()
        baseline.cp.get_default_memory_pool().free_all_blocks()
    return {
        "task": task_id,
        "input_sha256": task.input_sha256,
        "output_sha256": output_sha256,
        "device_source_sha256": hashlib.sha256(device_source.read_bytes()).hexdigest(),
        "ptx_sha256": hashlib.sha256(ptx).hexdigest(),
        "pyoptix_repository_commit": baseline.PYOPTIX_COMMIT,
        "optix_api_version": ".".join(str(value) for value in baseline.optix.version()),
        "complete_execution_call_count": complete_execution_call_count,
        "oracle_exact": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--execution-authority", type=Path, required=True)
    parser.add_argument("--device-source", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prereg, authority = load_execution_authority(
        args.execution_authority,
        preregistration_path=args.preregistration,
        root=ROOT,
        require_clean_repository=True,
    )
    device_source = require_bound_path(authority, "device_source", args.device_source)
    optix_include = require_bound_path(authority, "optix_include", args.optix_include)
    cuda_include = require_bound_path(authority, "cuda_include", args.cuda_include)
    if args.optix_sdk != authority["toolchain"]["optix_sdk"]:
        raise RuntimeError("OptiX SDK differs from execution authority")
    require_idle_bound_gpu(authority)

    from experiments.goal5796_matched import pyoptix_baseline as baseline

    if tuple(int(part) for part in args.optix_sdk.split(".")) != tuple(
        int(part) for part in baseline.optix.version()
    ):
        raise RuntimeError("PyOptiX API version differs from execution authority")
    if baseline.cp.__version__ != authority["host"]["cupy"]:
        raise RuntimeError("CuPy version differs from execution authority")
    if baseline.PYOPTIX_COMMIT != authority["pyoptix"]["repository_commit"]:
        raise RuntimeError("PyOptiX repository identity differs from authority")
    if (
        importlib.metadata.version(authority["pyoptix"]["distribution_name"])
        != (authority["pyoptix"]["distribution_version"])
    ):
        raise RuntimeError("PyOptiX distribution identity differs from authority")

    # Compile once so the two task executions consume the exact same PTX bytes;
    # repeated NVRTC calls can differ in non-semantic generated comments.
    ptx = baseline.compile_ptx(device_source, optix_include, cuda_include)
    rows = [
        execute_task(
            task_id,
            device_source=device_source,
            ptx=ptx,
        )
        for task_id in BASELINE_TASKS
    ]
    result: dict[str, object] = {
        "schema": PYOPTIX_IDENTITY_WITNESS_SCHEMA,
        "status": (
            "PASS__PYOPTIX_PACKAGE_FRONT_DOOR_REPEATED_LIFECYCLE_NO_TIMING_OBSERVED"
        ),
        "source_commit": authority["source_commit"],
        "preregistration_sha256": prereg["preregistration_sha256"],
        "execution_authority_sha256": authority["authority_sha256"],
        "hardware": authority["hardware"],
        "tasks": rows,
        "task_count": len(rows),
        "gpu_complete_execution_call_count": sum(
            row["complete_execution_call_count"] for row in rows
        ),
        "optix_launch_count": 3 * (STEADY_WARMUPS + STEADY_REPETITIONS),
        "registered_timing_observation_count": 0,
        "clock_api_called_by_witness_module": False,
        "duration_field_count": 0,
        "performance_claim_authorized": False,
    }
    result["witness_sha256"] = digest(result)
    create_json(args.output, result)
    print(json.dumps(result, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
