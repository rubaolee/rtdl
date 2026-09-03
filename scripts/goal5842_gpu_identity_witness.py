#!/usr/bin/env python3
"""Non-timed GPU identity and correctness witness for Goal5842 on/off arms."""

from __future__ import annotations

import argparse
import json
from collections.abc import Mapping
from pathlib import Path

from experiments.goal5842_causal_admission.contracts import (
    ADMISSION_TASKS,
    BASELINE_TASKS,
    GPU_IDENTITY_WITNESS_SCHEMA,
    SPHERE_TASK,
    STEADY_REPETITIONS,
    STEADY_WARMUPS,
    digest,
)
from experiments.goal5842_causal_admission.runtime import (
    bind_authorized_native_library,
    create_json,
    load_execution_authority,
    require_bound_path,
    require_idle_bound_gpu,
)
from experiments.goal5842_causal_admission.tasks import (
    build_task,
    checker_off_program,
    program_signature,
)
from rtdsl.v4 import V4Target, V4Toolchain
from rtdsl.v4_public_builtin_sphere import V4SphereTarget

ROOT = Path(__file__).resolve().parents[1]
GENERIC_LIFECYCLE_SCHEMA = "rtdl.generic_family_lifecycle.v1"
APPLICATION_PROVIDER_LIFECYCLE_SCHEMA = "rtdl.v4.prepared_application_lifecycle.v1"
SPHERE_PROVIDER_LIFECYCLE_SCHEMA = "rtdl.v4.prepared_builtin_sphere_owner.v1"


def report_progress(task_id: str, phase: str) -> None:
    """Emit untimed progress without adding an observation clock."""

    print(
        json.dumps(
            {
                "schema": "rtdl.goal5842.gpu_identity_witness_progress.v1",
                "task": task_id,
                "phase": phase,
            },
            sort_keys=True,
        ),
        flush=True,
    )


def thaw(value: object) -> object:
    if isinstance(value, Mapping):
        return {str(key): thaw(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [thaw(item) for item in value]
    return value


def provider_lifecycle_evidence(
    lifecycle_receipt: object,
    *,
    expected_execution_count: int,
    expected_provider_schema: str,
) -> dict[str, object]:
    """Validate the generic wrapper and extract its provider-owned count."""

    lifecycle = thaw(lifecycle_receipt)
    if not isinstance(lifecycle, dict):
        raise TypeError("prepared lifecycle receipt is not an object")
    if lifecycle.get("schema") != GENERIC_LIFECYCLE_SCHEMA:
        raise RuntimeError("generic prepared lifecycle schema mismatch")
    provider = lifecycle.get("provider_receipt")
    if not isinstance(provider, dict):
        raise TypeError("generic lifecycle provider receipt is missing")
    if provider.get("schema") != expected_provider_schema:
        raise RuntimeError("provider prepared lifecycle schema mismatch")
    execution_count = provider.get("execution_count")
    if (
        not isinstance(execution_count, int)
        or isinstance(execution_count, bool)
        or execution_count != expected_execution_count
    ):
        raise RuntimeError("prepared lifecycle execution count mismatch")
    return {
        "generic_lifecycle_schema": lifecycle["schema"],
        "provider_lifecycle_schema": provider["schema"],
        "prepared_lifecycle_execution_count": execution_count,
    }


def execute_and_check(
    prepared: object, task: object, complete_execution_call_count: int
) -> dict[str, object]:
    latest = None
    latest_output = None
    latest_full_output = None
    for _ in range(complete_execution_call_count):
        result = prepared.execute(task.batch)
        output = thaw(result.output)
        expected = thaw(task.expected_output)
        if task.task_id.endswith("TRIANGLE_WEIGHTED_ALL_HIT_V1"):
            per_ray = thaw(tuple(result.details["per_ray_u64"]))
            full_output = {"weighted_sum": output, "per_ray": per_ray}
            if full_output != expected:
                raise RuntimeError("triangle full output mismatch")
        else:
            full_output = output
            if output != expected:
                raise RuntimeError(f"output mismatch for {task.task_id}")
        receipt = thaw(result.traversal_receipt)
        if (
            receipt.get("physical_executor_classification")
            != "optix_traversal_observed"
        ):
            raise RuntimeError("identity witness did not observe OptiX traversal")
        latest = result
        latest_output = output
        latest_full_output = full_output
    if latest is None:
        raise RuntimeError("identity witness executed zero calls")
    lifecycle = provider_lifecycle_evidence(
        prepared.lifecycle_receipt,
        expected_execution_count=complete_execution_call_count,
        expected_provider_schema=(
            SPHERE_PROVIDER_LIFECYCLE_SCHEMA
            if task.task_id == SPHERE_TASK
            else APPLICATION_PROVIDER_LIFECYCLE_SCHEMA
        ),
    )
    return {
        "output": latest_output,
        "output_sha256": latest.output_sha256,
        "full_output_sha256": digest(latest_full_output),
        "traversal_receipt_sha256": digest(receipt),
        "physical_executor_classification": receipt["physical_executor_classification"],
        "complete_execution_call_count": complete_execution_call_count,
        **lifecycle,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--preregistration", type=Path, required=True)
    parser.add_argument("--execution-authority", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    prereg, authority = load_execution_authority(
        args.execution_authority,
        preregistration_path=args.preregistration,
        root=ROOT,
        require_clean_repository=True,
    )
    if args.compute_capability != authority["hardware"]["compute_capability"]:
        raise RuntimeError("compute capability differs from execution authority")
    native = bind_authorized_native_library(authority, args.native)
    for key, supplied in (
        ("optix_include", args.optix_include),
        ("cuda_include", args.cuda_include),
    ):
        require_bound_path(authority, key, supplied)
    if args.optix_sdk != authority["toolchain"]["optix_sdk"]:
        raise RuntimeError("OptiX SDK argument differs from execution authority")
    require_idle_bound_gpu(authority)
    capability = tuple(int(part) for part in args.compute_capability.split("."))
    toolchain = V4Toolchain.current(
        compute_capability=capability,
        optix_include=args.optix_include,
        cuda_include=args.cuda_include,
    )
    rows = []
    for task_id in ADMISSION_TASKS:
        report_progress(task_id, "BUILD_TASK")
        task = build_task(task_id)
        route = task.route_factory()
        admitted = route.compile()
        bypass = checker_off_program(route)
        if program_signature(admitted) != program_signature(bypass):
            raise RuntimeError("target-neutral on/off identity mismatch")
        complete_execution_call_count = (
            STEADY_WARMUPS + STEADY_REPETITIONS if task_id in BASELINE_TASKS else 1
        )
        target = (
            V4SphereTarget.from_native(
                native,
                optix_sdk=args.optix_sdk,
                compute_capability=args.compute_capability,
            )
            if task_id == SPHERE_TASK
            else V4Target.from_native(
                native,
                optix_sdk=args.optix_sdk,
                compute_capability=args.compute_capability,
            )
        )
        report_progress(task_id, "MATERIALIZE_CHECK_ON")
        on_materialized = admitted.materialize(target=target, toolchain=toolchain)
        report_progress(task_id, "MATERIALIZE_CHECK_OFF")
        off_materialized = bypass.materialize(target=target, toolchain=toolchain)
        on_identity = on_materialized.identity.to_dict()
        off_identity = off_materialized.identity.to_dict()
        if on_identity != off_identity:
            raise RuntimeError("generated/native on/off identity mismatch")
        report_progress(task_id, "PREPARE_CHECK_ON")
        on_prepared = on_materialized.prepare(task.static_input)
        try:
            report_progress(task_id, "EXECUTE_CHECK_ON")
            on_result = execute_and_check(
                on_prepared, task, complete_execution_call_count
            )
        finally:
            on_prepared.close()
        report_progress(task_id, "PREPARE_CHECK_OFF")
        off_prepared = off_materialized.prepare(task.static_input)
        try:
            report_progress(task_id, "EXECUTE_CHECK_OFF")
            off_result = execute_and_check(
                off_prepared, task, complete_execution_call_count
            )
        finally:
            off_prepared.close()
        if on_result["output_sha256"] != off_result["output_sha256"]:
            raise RuntimeError("on/off output identity mismatch")
        if on_result["full_output_sha256"] != off_result["full_output_sha256"]:
            raise RuntimeError("on/off full output identity mismatch")
        rows.append(
            {
                "task": task_id,
                "input_sha256": task.input_sha256,
                "program_signature": program_signature(admitted),
                "executable_identity": on_identity,
                "on": on_result,
                "off": off_result,
                "exact_identity_equal": True,
            }
        )
        report_progress(task_id, "TASK_COMPLETE")
    result: dict[str, object] = {
        "schema": GPU_IDENTITY_WITNESS_SCHEMA,
        "status": "PASS__IDENTITY_AND_REPEATED_LIFECYCLE_NO_TIMING_OBSERVED",
        "source_commit": authority["source_commit"],
        "preregistration_sha256": prereg["preregistration_sha256"],
        "execution_authority_sha256": authority["authority_sha256"],
        "hardware": authority["hardware"],
        "native_library_sha256": authority["execution_paths"]["native_library_sha256"],
        "tasks": rows,
        "task_count": len(rows),
        "all_exact_identity_equal": all(row["exact_identity_equal"] for row in rows),
        "registered_timing_observation_count": 0,
        "gpu_complete_execution_call_count": sum(
            row[arm]["complete_execution_call_count"]
            for row in rows
            for arm in ("on", "off")
        ),
        "repeated_lifecycle_calls_per_baseline_task_arm": (
            STEADY_WARMUPS + STEADY_REPETITIONS
        ),
        "clock_api_called_by_witness_module": False,
        "duration_field_count": 0,
        "performance_claim_authorized": False,
    }
    result["witness_sha256"] = digest(result)
    create_json(args.output, result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
