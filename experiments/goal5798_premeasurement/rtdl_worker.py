#!/usr/bin/env python3
"""Phase-instrumented RTDL public-lifecycle arm for Goal5798."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

from worker_common import (
    MEMORY_MODE,
    PREPARED_REPETITIONS,
    PREPARED_WARMUPS,
    admit,
    create_json,
    finish_receipt,
    load_runtime_manifest,
    measured,
    now_ns,
    parser_for,
    plan_result,
    sha256_file,
    wait_memory_barrier,
)
from workload import digest, relation_workload, triangle_workload


ARM = "D_RTDL_PUBLIC"
RELATION_TASK = "CUSTOM_AABB_CLOSED_RELATION_COUNT_V1"
TRIANGLE_TASK = "BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1"


def main() -> None:
    parser = parser_for(ARM)
    parser.add_argument("--native", type=Path)
    parser.add_argument("--optix-include", type=Path)
    parser.add_argument("--cuda-include", type=Path)
    parser.add_argument("--optix-sdk")
    parser.add_argument("--compute-capability")
    parser.add_argument("--proof", type=Path)
    args = parser.parse_args()
    freeze, row, authority = admit(args)
    runtime = load_runtime_manifest(args.runtime_manifest.resolve(), verify_files=False)
    if args.plan_only:
        print(json.dumps(plan_result(
            freeze=freeze, row=row, runtime_manifest=runtime, arm=ARM,
        ), sort_keys=True))
        return
    required = ("native", "optix_include", "cuda_include", "optix_sdk", "compute_capability", "proof")
    for name in required:
        if getattr(args, name) is None:
            raise ValueError(f"execution requires --{name.replace('_', '-')}")
    capability_parts = args.compute_capability.split(".")
    if len(capability_parts) != 2 or any(
            not value.isdigit() for value in capability_parts):
        raise ValueError("RTDL worker requires an observed major.minor compute capability")
    selected = authority["host_binding"]["selected_stack"]
    if args.optix_sdk != selected["optix_api_version"]:
        raise ValueError("RTDL OptiX SDK differs from the selected compatible stack")
    if args.compute_capability != authority["host_binding"]["compute_capability"]:
        raise ValueError("RTDL compute target differs from the bound physical GPU")
    compute_capability = tuple(int(value) for value in capability_parts)

    repository = Path(__file__).resolve().parents[2]
    source = repository / "src"
    if str(source) not in sys.path:
        sys.path.insert(0, str(source))
    # This is the complete import list.  No RTDL private/advanced provider or
    # raw PTX/pipeline/SBT API is imported by this arm.
    from rtdsl.v4 import (
        AnyHitProtocolProof,
        BoundedRelationBatch,
        BoundedRelationProtocol,
        BoundedRelationStaticInput,
        TriangleReductionBatch,
        TriangleReductionMode,
        TriangleReductionProtocol,
        TriangleReductionStaticInput,
        V4Target,
        V4Toolchain,
        compile_protocol_program,
        standard_protocol_physical_plan,
    )

    phases: dict[str, int | None] = {
        "deterministic_input_materialization": 0,
        "protocol_validation_and_codegen": 0,
        # The public API exposes target materialize and static prepare totals.
        # It does not expose an internal split between NVRTC and module/SBT;
        # inventing that split would be false precision.
        "device_compile": None,
        "module_program_pipeline_sbt": None,
        "public_target_materialize_combined": 0,
        "gas_and_static_prepare": 0,
        "common_preparation_total": 0,
        "close": 0,
    }

    def materialize_input():
        task = relation_workload() if row["task"] == RELATION_TASK else triangle_workload()
        target = V4Target.from_native(
            args.native.resolve(), optix_sdk=args.optix_sdk,
            compute_capability=args.compute_capability)
        toolchain = V4Toolchain.current(
            compute_capability=compute_capability,
            optix_include=args.optix_include.resolve(),
            cuda_include=args.cuda_include.resolve())
        if row["task"] == RELATION_TASK:
            protocol = BoundedRelationProtocol(
                capacity=int(task["capacity"]),
                minimum_overlap_f32=float(task["minimum_overlap"]))
            static_input = BoundedRelationStaticInput(
                tuple(tuple(value) for value in task["indexed"]))
            batch = BoundedRelationBatch(
                tuple(tuple(value) for value in task["sources"]),
                expected_rows=tuple(tuple(value) for value in task["expected_rows"]))
        else:
            protocol = TriangleReductionProtocol(TriangleReductionMode.WEIGHTED_HIT_COUNT)
            vertices = tuple(tuple(value) for value in task["vertices"])
            static_input = TriangleReductionStaticInput(
                vertices=vertices,
                triangles=tuple((index, index + 1, index + 2)
                                for index in range(0, len(vertices), 3)),
                primitive_metadata={}, event_capacity=len(task["expected_per_ray"]))
            batch = TriangleReductionBatch(
                queries=tuple((tuple(origin), tuple(direction), float(task["tmax"]))
                              for origin, direction in task["rays"]),
                query_metadata={"query.weight": tuple(task["weights"])})
        return task, target, toolchain, protocol, static_input, batch

    input_state, phases["deterministic_input_materialization"] = measured(materialize_input)
    task_value, target, toolchain, protocol, static_input, batch = input_state
    preparation_start = now_ns()

    def validate_and_codegen():
        plan = standard_protocol_physical_plan(protocol)
        proof = AnyHitProtocolProof(
            callback_ir_sha256=plan.callback_ir_sha256,
            effect_digest=plan.effect_digest,
            proof_sha256=sha256_file(args.proof.resolve()),
            proof_kind="external_machine_checked_order_independence_v1")
        return compile_protocol_program(
            protocol, physical_plan=plan, any_hit_proof=proof)

    verified, phases["protocol_validation_and_codegen"] = measured(validate_and_codegen)
    materialized, phases["public_target_materialize_combined"] = measured(
        lambda: verified.materialize(target=target, toolchain=toolchain))
    prepared, phases["gas_and_static_prepare"] = measured(
        lambda: materialized.prepare(static_input))
    phases["common_preparation_total"] = now_ns() - preparation_start
    expected_relation_rows = (
        tuple(tuple(value) for value in task_value["expected_rows"])
        if row["task"] == RELATION_TASK else None)
    expected_per_ray = (
        tuple(task_value["expected_per_ray"])
        if row["task"] != RELATION_TASK else None)

    def complete_execute() -> dict[str, Any]:
        result = prepared.execute(
            batch,
            include_diagnostics=(row["task"] == TRIANGLE_TASK),
        )
        if row["task"] == RELATION_TASK:
            output = result.output
            if output != expected_relation_rows:
                raise RuntimeError("RTDL formal relation oracle mismatch")
            return {
                "result": result, "output": output,
                "raw_event_count": int(result.details["raw_event_count"]),
                "duplicate_count": int(result.details["duplicate_count"]),
            }
        per_ray = tuple(result.details["per_ray_u64"])
        weighted = int(result.output)
        if per_ray != expected_per_ray \
                or weighted != task_value["expected_weighted_sum"]:
            raise RuntimeError("RTDL formal triangle oracle mismatch")
        return {"result": result, "per_ray": per_ray, "weighted_sum": weighted}

    durations: list[int] = []
    latest: dict[str, Any] | None = None
    if row["mode"] == "PREPARED_EXECUTION":
        for _ in range(PREPARED_WARMUPS):
            latest = complete_execute()
        for _ in range(PREPARED_REPETITIONS):
            latest, elapsed = measured(complete_execute)
            durations.append(elapsed)
    elif row["mode"] == MEMORY_MODE:
        for _ in range(PREPARED_WARMUPS):
            latest = complete_execute()
        wait_memory_barrier(args.barrier_dir, {
            "schema": "rtdl.goal5798.prepared_memory_barrier.v1",
            "worker_id": row["worker_id"], "pid": os.getpid(),
            "arm": ARM, "task": row["task"],
            "executable_identity_sha256": prepared.identity.identity_sha256,
        })
        latest, elapsed = measured(complete_execute)
        durations.append(elapsed)
    else:
        latest, elapsed = measured(complete_execute)
        durations.append(elapsed)
    if latest is None:
        raise RuntimeError("worker produced no correctness result")
    result = latest["result"]
    lifecycle = prepared.lifecycle_receipt
    if row["task"] == RELATION_TASK:
        correctness = {
            "oracle_exact": True,
            "canonical_row_count": len(latest["output"]),
            "output_sha256": digest(latest["output"]),
            "expected_output_sha256": digest(task_value["expected_rows"]),
            "raw_output_sha256": digest(latest["output"]),
            "raw_event_count": latest["raw_event_count"],
            "raw_event_capacity": 8194,
            "duplicate_count": latest["duplicate_count"],
            "device_status": [dict(value) for value in result.launch_status],
        }
    else:
        correctness = {
            "oracle_exact": True,
            "per_ray_count": len(latest["per_ray"]),
            "per_ray_sha256": digest(latest["per_ray"]),
            "expected_per_ray_sha256": digest(task_value["expected_per_ray"]),
            "weighted_sum": latest["weighted_sum"],
            "expected_weighted_sum": task_value["expected_weighted_sum"],
            "device_status": [dict(value) for value in result.launch_status],
            "raw_output_sha256": digest({
                "per_ray": latest["per_ray"], "weighted_sum": latest["weighted_sum"]}),
        }
    close_start = now_ns()
    prepared.close()
    prepared.close()
    phases["close"] = now_ns() - close_start
    import resource
    host_rusage_maxrss_bytes = int(
        resource.getrusage(resource.RUSAGE_SELF).ru_maxrss) * 1024
    receipt = finish_receipt(
        freeze=freeze, row=row, runtime_manifest=runtime, authority=authority,
        phases_ns=phases, execute_durations_ns=durations,
        correctness=correctness,
        implementation={
            "arm": ARM,
            "public_import_module": "rtdsl.v4",
            "private_or_advanced_provider_import_count": 0,
            "manual_ptx_pipeline_sbt_escape_count": 0,
            "program_identity_sha256": verified.identity.identity_sha256,
            "executable_identity_sha256": result.executable_identity.identity_sha256,
            "output_identity_sha256": result.output_sha256,
            "traversal_receipt": result.traversal_receipt,
            "lifecycle_receipt": lifecycle,
            "native_sha256": hashlib.sha256(args.native.read_bytes()).hexdigest(),
            "proof_carrier_sha256": hashlib.sha256(args.proof.read_bytes()).hexdigest(),
            "public_phase_split_limit": (
                "materialize exposes one combined target-compile total; prepare exposes one "
                "combined module-pipeline-SBT-GAS/static total"),
            "host_rusage_maxrss_bytes": host_rusage_maxrss_bytes,
        },
    )
    create_json(args.output, receipt)
    print(json.dumps(receipt, sort_keys=True))


if __name__ == "__main__":
    main()
