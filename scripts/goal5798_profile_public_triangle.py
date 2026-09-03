#!/usr/bin/env python3
"""Untimed-claim diagnostic for the V4 public prepared triangle lifecycle."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import statistics
import time

from rtdsl.v4 import (
    AnyHitProtocolProof,
    TriangleReductionBatch,
    TriangleReductionMode,
    TriangleReductionProtocol,
    TriangleReductionStaticInput,
    V4Target,
    V4Toolchain,
    compile_protocol_program,
    standard_protocol_physical_plan,
)


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def measured(action):
    started = time.perf_counter_ns()
    value = action()
    return value, time.perf_counter_ns() - started


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--proof", type=Path, required=True)
    parser.add_argument("--warmups", type=int, default=8)
    parser.add_argument("--repetitions", type=int, default=64)
    parser.add_argument("--goal5798-scale", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    if args.warmups < 1 or args.repetitions < 1:
        raise ValueError("positive warmup and repetition counts required")

    spec = json.loads(args.spec.read_bytes())
    if args.goal5798_scale:
        from experiments.goal5798_premeasurement.workload import triangle_workload

        task = triangle_workload()
    else:
        task = spec["tasks"]["BUILTIN_TRIANGLE_WEIGHTED_ALL_HIT_V1"]
    protocol = TriangleReductionProtocol(TriangleReductionMode.WEIGHTED_HIT_COUNT)
    plan = standard_protocol_physical_plan(protocol)
    proof = AnyHitProtocolProof(
        callback_ir_sha256=plan.callback_ir_sha256,
        effect_digest=plan.effect_digest,
        proof_sha256=file_sha256(args.proof),
        proof_kind="external_machine_checked_order_independence_v1",
    )
    target = V4Target.from_native(
        args.native,
        optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability,
    )
    toolchain = V4Toolchain.current(
        compute_capability=tuple(map(int, args.compute_capability.split("."))),
        optix_include=args.optix_include,
        cuda_include=args.cuda_include,
    )
    verified = compile_protocol_program(
        protocol, physical_plan=plan, any_hit_proof=proof)
    materialized, materialize_ns = measured(
        lambda: verified.materialize(target=target, toolchain=toolchain))
    vertices = tuple(tuple(row) for row in task["vertices"])
    triangles = tuple(
        (index, index + 1, index + 2)
        for index in range(0, len(vertices), 3))
    prepared, prepare_ns = measured(lambda: materialized.prepare(
        TriangleReductionStaticInput(
            vertices=vertices,
            triangles=triangles,
            primitive_metadata={},
            event_capacity=sum(int(value) for value in task["expected_per_ray"]),
        )))
    batch = TriangleReductionBatch(
        queries=tuple(
            (tuple(origin), tuple(direction), float(task["tmax"]))
            for origin, direction in task["rays"]),
        query_metadata={"query.weight": tuple(task["weights"])},
    )

    api_samples = []
    oracle_samples = []

    def execute_checked():
        result, api_elapsed = measured(
            lambda: prepared.execute(batch, include_diagnostics=True)
        )
        oracle_started = time.perf_counter_ns()
        if list(result.details["per_ray_u64"]) != task["expected_per_ray"] \
                or int(result.output) != int(task["expected_weighted_sum"]):
            raise RuntimeError("public prepared triangle output mismatch")
        oracle_elapsed = time.perf_counter_ns() - oracle_started
        api_samples.append(api_elapsed)
        oracle_samples.append(oracle_elapsed)
        return result

    latest = None
    for _ in range(args.warmups):
        latest = execute_checked()
    samples = []
    for _ in range(args.repetitions):
        latest, elapsed = measured(execute_checked)
        samples.append(elapsed)
    assert latest is not None
    statuses, status_materialize_ns = measured(
        lambda: tuple(dict(row) for row in latest.launch_status))
    reducer_rows, reducer_materialize_ns = measured(
        lambda: tuple(dict(row) for row in latest.details["raw_reducer_rows"]))
    if any(row["first_error_claimed"] or row["error_code"] for row in statuses):
        raise RuntimeError("diagnostic observed a device status failure")
    lifecycle = prepared.lifecycle_receipt
    prepared.close()
    prepared.close()
    result = {
        "schema": "rtdl.goal5798.public_triangle_performance_diagnostic.v1",
        "status": "PASS",
        "claim_scope": "UNREGISTERED_ENGINEERING_DIAGNOSTIC__NOT_FORMAL_PERFORMANCE",
        "native_sha256": file_sha256(args.native),
        "ray_count": len(task["rays"]),
        "warmup_count": args.warmups,
        "repetition_count": args.repetitions,
        "materialize_ns": materialize_ns,
        "prepare_ns": prepare_ns,
        "execute_median_ns": statistics.median(samples),
        "execute_min_ns": min(samples),
        "execute_max_ns": max(samples),
        "public_api_median_ns": statistics.median(
            api_samples[-args.repetitions:]),
        "oracle_materialization_and_compare_median_ns": statistics.median(
            oracle_samples[-args.repetitions:]),
        "status_row_count": len(statuses),
        "status_materialize_once_ns": status_materialize_ns,
        "reducer_row_count": len(reducer_rows),
        "reducer_materialize_once_ns": reducer_materialize_ns,
        "output_exact": True,
        "physical_executor_classification": latest.traversal_receipt[
            "physical_executor_classification"],
        "lifecycle": lifecycle,
        "registered_performance_timing_count": 0,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(json.dumps(
        result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
