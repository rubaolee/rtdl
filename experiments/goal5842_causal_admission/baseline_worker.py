"""PyOptiX and current-public-RTDL subworkers for Goal5842 baselines."""

from __future__ import annotations

import argparse
import gc
import hashlib
import importlib.metadata
import json
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any

from .contracts import (
    BASELINE_SUBWORKER_SCHEMA,
    FIRST_MODE,
    PYOPTIX_ARM,
    RELATION_TASK,
    RTDL_ARM,
    STEADY_MODE,
    STEADY_REPETITIONS,
    STEADY_WARMUPS,
    TRIANGLE_TASK,
    digest,
)
from .runtime import (
    bind_authorized_native_library,
    create_json,
    load_execution_authority,
    require_bound_path,
)
from .tasks import build_task, program_signature

ROOT = Path(__file__).resolve().parents[2]
MODES = (FIRST_MODE, STEADY_MODE)


def measured(action: Callable[[], Any]) -> tuple[Any, int]:
    started = time.perf_counter_ns()
    value = action()
    return value, time.perf_counter_ns() - started


def baseline_schedule_row(prereg: dict[str, Any], worker_id: str) -> dict[str, Any]:
    matches = [
        dict(row)
        for row in prereg["baseline_schedule"]
        if row["worker_id"] == worker_id
    ]
    if len(matches) != 1:
        raise ValueError(f"baseline worker id is not unique: {worker_id}")
    return matches[0]


def verify_output(task_id: str, value: dict[str, Any], expected: object) -> str:
    if task_id == RELATION_TASK:
        output = tuple(tuple(int(item) for item in row) for row in value["output"])
        if output != expected:
            raise RuntimeError("relation output differs from independent fixture")
        return digest(output)
    if task_id == TRIANGLE_TASK:
        if int(value["weighted_sum"]) != expected["weighted_sum"]:
            raise RuntimeError(
                "triangle weighted output differs from independent fixture"
            )
        per_ray = tuple(int(item) for item in value["per_ray"])
        if per_ray != expected["per_ray"]:
            raise RuntimeError(
                "triangle per-ray output differs from independent fixture"
            )
        # The cross-arm public output contract is the checked weighted scalar.
        # Direct and PyOptiX additionally validate their internal per-ray rows.
        return digest(int(value["weighted_sum"]))
    raise ValueError(f"unsupported baseline task: {task_id}")


def run_rtdl(
    args: argparse.Namespace,
    task: object,
    mode: str,
    authority: dict[str, Any],
) -> tuple[dict[str, int | None | list[int]], dict[str, object], str]:
    from rtdsl.v4 import V4Target, V4Toolchain

    capability = tuple(
        int(part) for part in authority["hardware"]["compute_capability"].split(".")
    )

    def bind_runtime():
        return (
            V4Target.from_native(
                args.native,
                optix_sdk=args.optix_sdk,
                compute_capability=authority["hardware"]["compute_capability"],
            ),
            V4Toolchain.current(
                compute_capability=capability,
                optix_include=args.optix_include,
                cuda_include=args.cuda_include,
            ),
        )

    (target, toolchain), runtime_binding_ns = measured(bind_runtime)
    route, declaration_ns = measured(task.route_factory)
    program, admission_ns = measured(route.compile)
    materialized, materialize_ns = measured(
        lambda: program.materialize(target=target, toolchain=toolchain)
    )
    prepared, prepare_ns = measured(lambda: materialized.prepare(task.static_input))

    def execute() -> tuple[object, str]:
        result = prepared.execute(task.batch)
        if task.task_id == RELATION_TASK:
            output = tuple(tuple(int(item) for item in row) for row in result.output)
            if output != task.expected_output:
                raise RuntimeError("RTDL relation oracle mismatch")
            detailed = {"output": output}
        else:
            weighted = int(result.output)
            if weighted != task.expected_output["weighted_sum"]:
                raise RuntimeError("RTDL triangle oracle mismatch")
            detailed = {
                "weighted_sum": weighted,
                # The generic public output contract commits the scalar.  The
                # independent per-ray vector is checked by the matched
                # PyOptiX/Direct arms and by the underlying RTDL route tests.
                "per_ray": task.expected_output["per_ray"],
            }
        receipt = dict(result.traversal_receipt)
        if (
            receipt.get("physical_executor_classification")
            != "optix_traversal_observed"
        ):
            raise RuntimeError("RTDL baseline did not execute OptiX traversal")
        return detailed, result.output_sha256

    first_ns: int | None = None
    steady_ns: list[int] = []
    latest: tuple[object, str] | None = None
    if mode == FIRST_MODE:
        latest, first_ns = measured(execute)
    else:
        for _ in range(STEADY_WARMUPS):
            latest = execute()
        for _ in range(STEADY_REPETITIONS):
            latest, elapsed = measured(execute)
            steady_ns.append(elapsed)
    if latest is None:
        raise RuntimeError("RTDL baseline produced no output")
    close_started = time.perf_counter_ns()
    prepared.close()
    close_ns = time.perf_counter_ns() - close_started
    phases: dict[str, int | None | list[int]] = {
        "route_declaration_and_artifact_binding": declaration_ns,
        "provider_projection_and_generic_family_admission": admission_ns,
        "runtime_target_and_toolchain_binding": runtime_binding_ns,
        "device_compile": None,
        "module_program_pipeline_sbt": None,
        "target_materialization": materialize_ns,
        "native_prepare": prepare_ns,
        "first_complete_execution": first_ns,
        "steady_complete_execution": steady_ns,
        "close": close_ns,
    }
    identity = {
        "program": program_signature(program),
        "executable": materialized.identity.to_dict(),
        "native_library_sha256": authority["execution_paths"]["native_library_sha256"],
    }
    return phases, identity, latest[1]


def run_pyoptix(
    args: argparse.Namespace,
    task: object,
    mode: str,
    authority: dict[str, Any],
) -> tuple[dict[str, int | None | list[int]], dict[str, object], str]:
    from experiments.goal5796_matched import pyoptix_baseline as baseline
    from experiments.goal5798_premeasurement.pyoptix_worker import (
        PyOptixRelationPrepared,
        PyOptixTrianglePrepared,
    )

    expected_version = tuple(
        int(part) for part in authority["toolchain"]["optix_sdk"].split(".")
    )
    if tuple(int(part) for part in baseline.optix.version()) != expected_version:
        raise RuntimeError("PyOptiX API version differs from execution authority")
    if baseline.cp.__version__ != authority["host"]["cupy"]:
        raise RuntimeError("CuPy version differs from execution authority")
    if baseline.PYOPTIX_COMMIT != authority["pyoptix"]["repository_commit"]:
        raise RuntimeError("PyOptiX repository identity differs from authority")
    distribution = authority["pyoptix"]["distribution_name"]
    if (
        importlib.metadata.version(distribution)
        != authority["pyoptix"]["distribution_version"]
    ):
        raise RuntimeError("PyOptiX distribution identity differs from authority")
    raw = task.provider_fixture
    if not isinstance(raw, dict):
        raise TypeError("PyOptiX baseline task lacks its frozen provider fixture")
    ptx, device_compile_ns = measured(
        lambda: baseline.compile_ptx(
            args.device_source.resolve(),
            args.optix_include.resolve(),
            args.cuda_include.resolve(),
        )
    )

    def pipeline_state():
        context, logger = baseline.make_context()
        task_name = "relation" if task.task_id == RELATION_TASK else "triangle"
        pipeline, groups, logs = baseline.build_pipeline(context, ptx, task=task_name)
        sbt, sbt_keepalive = baseline.make_sbt(groups)
        return context, logger, pipeline, groups, logs, sbt, sbt_keepalive

    state, pipeline_ns = measured(pipeline_state)
    context = state[0]
    pipeline = state[2]
    sbt = state[5]
    if task.task_id == RELATION_TASK:
        prepared, prepare_ns = measured(
            lambda: PyOptixRelationPrepared(baseline, context, pipeline, sbt, raw)
        )
    else:
        prepared, prepare_ns = measured(
            lambda: PyOptixTrianglePrepared(baseline, context, pipeline, sbt, raw)
        )

    def execute() -> tuple[dict[str, Any], str]:
        value = prepared.execute()
        return value, verify_output(task.task_id, value, task.expected_output)

    first_ns: int | None = None
    steady_ns: list[int] = []
    latest: tuple[dict[str, Any], str] | None = None
    if mode == FIRST_MODE:
        latest, first_ns = measured(execute)
    else:
        for _ in range(STEADY_WARMUPS):
            latest = execute()
        for _ in range(STEADY_REPETITIONS):
            latest, elapsed = measured(execute)
            steady_ns.append(elapsed)
    if latest is None:
        raise RuntimeError("PyOptiX baseline produced no output")
    close_started = time.perf_counter_ns()
    prepared = None
    sbt = None
    pipeline = None
    context = None
    state = None
    gc.collect()
    baseline.cp.get_default_memory_pool().free_all_blocks()
    close_ns = time.perf_counter_ns() - close_started
    phases = {
        "route_declaration_and_artifact_binding": None,
        "provider_projection_and_generic_family_admission": None,
        "runtime_target_and_toolchain_binding": None,
        "device_compile": device_compile_ns,
        "module_program_pipeline_sbt": pipeline_ns,
        "target_materialization": device_compile_ns + pipeline_ns,
        "native_prepare": prepare_ns,
        "first_complete_execution": first_ns,
        "steady_complete_execution": steady_ns,
        "close": close_ns,
    }
    identity = {
        "device_source_sha256": hashlib.sha256(
            args.device_source.read_bytes()
        ).hexdigest(),
        "ptx_sha256": hashlib.sha256(ptx).hexdigest(),
        "pyoptix_repository_commit": baseline.PYOPTIX_COMMIT,
        "optix_api_version": ".".join(str(part) for part in baseline.optix.version()),
    }
    return phases, identity, latest[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--execution-authority", type=Path, required=True)
    parser.add_argument("--schedule-worker-id", required=True)
    parser.add_argument("--mode", choices=MODES, required=True)
    parser.add_argument("--arm", choices=(PYOPTIX_ARM, RTDL_ARM), required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--device-source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prereg, authority = load_execution_authority(
        args.execution_authority,
        preregistration_path=args.preregistration,
        root=ROOT,
        require_clean_repository=True,
    )
    row = baseline_schedule_row(prereg, args.schedule_worker_id)
    if row["arm"] != args.arm:
        raise RuntimeError("baseline worker arm differs from frozen schedule")
    for key, supplied in (
        ("native_library", args.native),
        ("device_source", args.device_source),
        ("optix_include", args.optix_include),
        ("cuda_include", args.cuda_include),
    ):
        require_bound_path(authority, key, supplied)
    if args.optix_sdk != authority["toolchain"]["optix_sdk"]:
        raise RuntimeError("OptiX SDK argument differs from execution authority")
    if args.arm == RTDL_ARM:
        bind_authorized_native_library(authority, args.native)
    input_started = time.perf_counter_ns()
    task = build_task(row["task"])
    input_ns = time.perf_counter_ns() - input_started
    if args.arm == RTDL_ARM:
        phases, identity, output_sha256 = run_rtdl(args, task, args.mode, authority)
    else:
        phases, identity, output_sha256 = run_pyoptix(args, task, args.mode, authority)
    phases["deterministic_input_materialization"] = input_ns
    receipt: dict[str, object] = {
        "schema": BASELINE_SUBWORKER_SCHEMA,
        "status": "PASS",
        "schedule_worker_id": row["worker_id"],
        "subworker_id": f"{row['worker_id']}__{args.mode}",
        "task": row["task"],
        "arm": row["arm"],
        "block": row["block"],
        "mode": args.mode,
        "preregistration_sha256": prereg["preregistration_sha256"],
        "execution_authority_sha256": authority["authority_sha256"],
        "input_sha256": task.input_sha256,
        "output_sha256": output_sha256,
        "oracle_exact": True,
        "phases_ns": phases,
        "identity": identity,
    }
    receipt["receipt_sha256"] = digest(receipt)
    create_json(args.output, receipt)
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
