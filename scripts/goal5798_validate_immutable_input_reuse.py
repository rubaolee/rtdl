#!/usr/bin/env python3
"""Correctness and performance diagnostic for Goal5798 immutable-input reuse.

This is deliberately an engineering diagnostic, not a registered performance
result.  It exercises the public lifecycle for A->A, A->B, B->A, A->A and
also calls each native successor ABI once before any upload to prove that an
unjustified reuse request fails closed.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import statistics
import time

import numpy as np

from experiments.goal5798_premeasurement.workload import (
    relation_workload,
    triangle_workload,
)
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
from rtdsl.v4_bounded_relation_optix_runtime import _Status as RelationStatus
from rtdsl.v4_bounded_relation_optix_runtime import _boxes
from rtdsl.v4_triangle_reduction_optix_runtime import _Status as TriangleStatus


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def elapsed_ns(action):
    started = time.perf_counter_ns()
    result = action()
    return result, time.perf_counter_ns() - started


def proof_for(protocol, proof_path: Path) -> AnyHitProtocolProof:
    plan = standard_protocol_physical_plan(protocol)
    return AnyHitProtocolProof(
        callback_ir_sha256=plan.callback_ir_sha256,
        effect_digest=plan.effect_digest,
        proof_sha256=sha256_file(proof_path),
        proof_kind="external_machine_checked_order_independence_v1",
    )


def require_native_reuse_rejection_relation(owner, source_boxes) -> str:
    bounds, ids = _boxes(source_boxes, "source_boxes")
    count = len(source_boxes)
    raw = ctypes.c_uint64()
    unique = ctypes.c_uint64()
    overflowed = ctypes.c_uint32()
    rows = (ctypes.c_uint32 * (owner._contract.capacity * 2))()
    statuses = (RelationStatus * (count + owner._indexed_count))()
    counters = (ctypes.c_uint64 * 7)()
    error = ctypes.create_string_buffer(16384)
    status = int(owner._execute(
        owner._token, bounds, ids, count, 1,
        ctypes.byref(raw), ctypes.byref(unique), ctypes.byref(overflowed),
        rows, statuses, counters, error, len(error)))
    message = error.value.decode("utf-8", errors="replace")
    if status == 0 or "source-cache reuse is invalid" not in message:
        raise RuntimeError(
            "bounded-relation native ABI accepted reuse without predecessor")
    return message


def require_native_reuse_rejection_triangle(owner, queries) -> str:
    count = len(queries)
    origins = np.ascontiguousarray(
        [origin for origin, _direction, _tmax in queries], dtype=np.float32)
    directions = np.ascontiguousarray(
        [direction for _origin, direction, _tmax in queries], dtype=np.float32)
    tmax = np.ascontiguousarray(
        [_tmax for _origin, _direction, _tmax in queries], dtype=np.float32)
    per_ray = (ctypes.c_uint64 * count)()
    event_count = ctypes.c_uint64()
    statuses = (TriangleStatus * count)()
    counters = (ctypes.c_uint64 * 7)()
    error = ctypes.create_string_buffer(16384)
    status = int(owner._execute(
        owner._token,
        origins.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
        directions.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
        tmax.ctypes.data_as(ctypes.POINTER(ctypes.c_float)),
        count, 1, per_ray, ctypes.byref(event_count),
        owner._event_query_host, owner._event_primitive_host,
        owner._event_stable_host, owner._event_signed_host,
        owner._event_include_host, statuses, counters, error, len(error)))
    message = error.value.decode("utf-8", errors="replace")
    if status == 0 or "reuse lacks an exact uploaded predecessor" not in message:
        raise RuntimeError("triangle native ABI accepted reuse without predecessor")
    return message


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--proof", type=Path, required=True)
    parser.add_argument("--warmups", type=int, default=8)
    parser.add_argument("--repetitions", type=int, default=64)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    if args.warmups < 1 or args.repetitions < 1:
        raise ValueError("positive warmup and repetition counts required")

    target = V4Target.from_native(
        args.native, optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability)
    compute_capability = tuple(map(int, args.compute_capability.split(".")))
    toolchain = V4Toolchain.current(
        compute_capability=compute_capability,
        optix_include=args.optix_include,
        cuda_include=args.cuda_include)

    relation = relation_workload()
    relation_protocol = BoundedRelationProtocol(
        capacity=int(relation["capacity"]),
        minimum_overlap_f32=float(relation["minimum_overlap"]))
    relation_program = compile_protocol_program(
        relation_protocol,
        physical_plan=standard_protocol_physical_plan(relation_protocol),
        any_hit_proof=proof_for(relation_protocol, args.proof))
    relation_materialized, relation_materialize_ns = elapsed_ns(
        lambda: relation_program.materialize(target=target, toolchain=toolchain))
    relation_prepared, relation_prepare_ns = elapsed_ns(
        lambda: relation_materialized.prepare(BoundedRelationStaticInput(
            tuple(tuple(row) for row in relation["indexed"]))))
    relation_a = BoundedRelationBatch(
        tuple(tuple(row) for row in relation["sources"]),
        expected_rows=tuple(tuple(row) for row in relation["expected_rows"]))
    relation_b_sources = list(relation_a.source_boxes)
    relation_b_sources[0] = (-100.0, 0.0, -99.0, 1.0, 0)
    relation_b_expected = tuple(relation_a.expected_rows[1:])
    relation_b = BoundedRelationBatch(
        tuple(relation_b_sources), expected_rows=relation_b_expected)
    relation_rejection = require_native_reuse_rejection_relation(
        relation_prepared._owner, relation_a.source_boxes)
    relation_outputs = []
    for label, batch, expected in (
        ("A_full", relation_a, relation_a.expected_rows),
        ("A_reuse", relation_a, relation_a.expected_rows),
        ("B_full", relation_b, relation_b_expected),
        ("A_restore_full", relation_a, relation_a.expected_rows),
        ("A_restore_reuse", relation_a, relation_a.expected_rows),
    ):
        observed = relation_prepared.execute(batch)
        if observed.output != expected:
            raise RuntimeError(f"relation transition {label} mismatch")
        relation_outputs.append({"transition": label, "row_count": len(observed.output)})
    relation_samples = []
    for _ in range(args.warmups):
        relation_prepared.execute(relation_a)
    for _ in range(args.repetitions):
        _value, duration = elapsed_ns(lambda: relation_prepared.execute(relation_a))
        relation_samples.append(duration)
    relation_formal_wrapper_samples = []

    def relation_formal_wrapper_execute():
        observed = relation_prepared.execute(relation_a)
        output = [list(value) for value in observed.output]
        if output != relation["expected_rows"]:
            raise RuntimeError("relation formal-wrapper oracle mismatch")
        return observed

    for _ in range(args.warmups):
        relation_formal_wrapper_execute()
    for _ in range(args.repetitions):
        _value, duration = elapsed_ns(relation_formal_wrapper_execute)
        relation_formal_wrapper_samples.append(duration)
    relation_expected_tuple = tuple(
        tuple(value) for value in relation["expected_rows"])
    relation_bulk_wrapper_samples = []

    def relation_bulk_wrapper_execute():
        observed = relation_prepared.execute(relation_a)
        if observed.output != relation_expected_tuple:
            raise RuntimeError("relation bulk-wrapper oracle mismatch")
        return observed

    for _ in range(args.warmups):
        relation_bulk_wrapper_execute()
    for _ in range(args.repetitions):
        _value, duration = elapsed_ns(relation_bulk_wrapper_execute)
        relation_bulk_wrapper_samples.append(duration)
    relation_lifecycle = relation_prepared.lifecycle_receipt
    relation_prepared.close()

    triangle = triangle_workload()
    triangle_protocol = TriangleReductionProtocol(
        TriangleReductionMode.WEIGHTED_HIT_COUNT)
    triangle_program = compile_protocol_program(
        triangle_protocol,
        physical_plan=standard_protocol_physical_plan(triangle_protocol),
        any_hit_proof=proof_for(triangle_protocol, args.proof))
    triangle_materialized, triangle_materialize_ns = elapsed_ns(
        lambda: triangle_program.materialize(target=target, toolchain=toolchain))
    vertices = tuple(tuple(row) for row in triangle["vertices"])
    triangles = tuple(
        (index, index + 1, index + 2)
        for index in range(0, len(vertices), 3))
    triangle_prepared, triangle_prepare_ns = elapsed_ns(
        lambda: triangle_materialized.prepare(TriangleReductionStaticInput(
            vertices=vertices, triangles=triangles, primitive_metadata={},
            event_capacity=len(triangle["expected_per_ray"]))))
    queries_a = tuple(
        (tuple(origin), tuple(direction), float(triangle["tmax"]))
        for origin, direction in triangle["rays"])
    weights = tuple(triangle["weights"])
    triangle_a = TriangleReductionBatch(
        queries=queries_a, query_metadata={"query.weight": weights})
    queries_b = list(queries_a)
    origin, direction, tmax = queries_b[0]
    queries_b[0] = ((origin[0], 1000.0, origin[2]), direction, tmax)
    queries_b = tuple(queries_b)
    triangle_b = TriangleReductionBatch(
        queries=queries_b, query_metadata={"query.weight": weights})
    triangle_rejection = require_native_reuse_rejection_triangle(
        triangle_prepared._owner, triangle_a.queries)
    expected_a = tuple(triangle["expected_per_ray"])
    expected_b = (0,) + expected_a[1:]
    triangle_outputs = []
    for label, batch, expected_per_ray, expected_sum in (
        ("A_full", triangle_a, expected_a, triangle["expected_weighted_sum"]),
        ("A_reuse", triangle_a, expected_a, triangle["expected_weighted_sum"]),
        ("B_full", triangle_b, expected_b,
         triangle["expected_weighted_sum"] - weights[0]),
        ("A_restore_full", triangle_a, expected_a,
         triangle["expected_weighted_sum"]),
        ("A_restore_reuse", triangle_a, expected_a,
         triangle["expected_weighted_sum"]),
    ):
        observed = triangle_prepared.execute(batch, include_diagnostics=True)
        per_ray = tuple(observed.details["per_ray_u64"])
        if per_ray != expected_per_ray or int(observed.output) != int(expected_sum):
            raise RuntimeError(f"triangle transition {label} mismatch")
        triangle_outputs.append({
            "transition": label, "per_ray_sum": sum(per_ray),
            "weighted_sum": int(observed.output),
        })
    triangle_samples = []
    for _ in range(args.warmups):
        triangle_prepared.execute(triangle_a, include_diagnostics=True)
    for _ in range(args.repetitions):
        _value, duration = elapsed_ns(
            lambda: triangle_prepared.execute(
                triangle_a, include_diagnostics=True
            )
        )
        triangle_samples.append(duration)
    triangle_complete_samples = []
    triangle_bulk_complete_samples = []

    def triangle_complete_execute():
        observed = triangle_prepared.execute(
            triangle_a, include_diagnostics=True
        )
        per_ray = [int(value) for value in observed.details["per_ray_u64"]]
        weighted = int(observed.output)
        if per_ray != triangle["expected_per_ray"] \
                or weighted != triangle["expected_weighted_sum"]:
            raise RuntimeError("triangle formal-wrapper oracle mismatch")
        return observed

    for _ in range(args.warmups):
        triangle_complete_execute()
    for _ in range(args.repetitions):
        _value, duration = elapsed_ns(triangle_complete_execute)
        triangle_complete_samples.append(duration)

    expected_per_ray_tuple = tuple(triangle["expected_per_ray"])

    def triangle_bulk_complete_execute():
        observed = triangle_prepared.execute(
            triangle_a, include_diagnostics=True
        )
        per_ray = tuple(observed.details["per_ray_u64"])
        weighted = int(observed.output)
        if per_ray != expected_per_ray_tuple \
                or weighted != triangle["expected_weighted_sum"]:
            raise RuntimeError("triangle bulk-wrapper oracle mismatch")
        return observed

    for _ in range(args.warmups):
        triangle_bulk_complete_execute()
    for _ in range(args.repetitions):
        _value, duration = elapsed_ns(triangle_bulk_complete_execute)
        triangle_bulk_complete_samples.append(duration)
    triangle_lifecycle = triangle_prepared.lifecycle_receipt
    triangle_identity = triangle_prepared.identity.identity_sha256
    triangle_contract_decision_sha256 = (
        triangle_prepared.protocol_contract_decision.to_mapping()["decision_sha256"]
        if hasattr(triangle_prepared, "protocol_contract_decision") else
        triangle_lifecycle["protocol_contract_decision_sha256"]
    )
    triangle_composed_ptx_sha256 = triangle_prepared._owner._composed_ptx_sha
    triangle_prepared.close()

    result = {
        "schema": "rtdl.goal5798.immutable_input_reuse_diagnostic.v1",
        "status": "PASS",
        "claim_scope": "OUTCOME_DIRECTED_ENGINEERING_DIAGNOSTIC__NOT_FORMAL_PERFORMANCE",
        "native_sha256": sha256_file(args.native),
        "host_stack_changed_from_formal_run": False,
        "registered_performance_timing_count": 0,
        "relation": {
            "native_unjustified_reuse_rejected": True,
            "native_rejection": relation_rejection,
            "transitions": relation_outputs,
            "materialize_ns": relation_materialize_ns,
            "prepare_ns": relation_prepare_ns,
            "prepared_public_execute_median_ns": statistics.median(relation_samples),
            "prepared_public_execute_min_ns": min(relation_samples),
            "prepared_public_execute_max_ns": max(relation_samples),
            "formal_wrapper_execute_median_ns": statistics.median(
                relation_formal_wrapper_samples),
            "formal_wrapper_execute_min_ns": min(relation_formal_wrapper_samples),
            "formal_wrapper_execute_max_ns": max(relation_formal_wrapper_samples),
            "bulk_wrapper_execute_median_ns": statistics.median(
                relation_bulk_wrapper_samples),
            "bulk_wrapper_execute_min_ns": min(relation_bulk_wrapper_samples),
            "bulk_wrapper_execute_max_ns": max(relation_bulk_wrapper_samples),
            "warmup_count": args.warmups,
            "repetition_count": args.repetitions,
            "lifecycle": relation_lifecycle,
        },
        "triangle": {
            "native_unjustified_reuse_rejected": True,
            "native_rejection": triangle_rejection,
            "transitions": triangle_outputs,
            "materialize_ns": triangle_materialize_ns,
            "prepare_ns": triangle_prepare_ns,
            "prepared_public_execute_median_ns": statistics.median(triangle_samples),
            "prepared_public_execute_min_ns": min(triangle_samples),
            "prepared_public_execute_max_ns": max(triangle_samples),
            "formal_wrapper_execute_median_ns": statistics.median(
                triangle_complete_samples),
            "formal_wrapper_execute_min_ns": min(triangle_complete_samples),
            "formal_wrapper_execute_max_ns": max(triangle_complete_samples),
            "bulk_wrapper_execute_median_ns": statistics.median(
                triangle_bulk_complete_samples),
            "bulk_wrapper_execute_min_ns": min(triangle_bulk_complete_samples),
            "bulk_wrapper_execute_max_ns": max(triangle_bulk_complete_samples),
            "executable_identity_sha256": triangle_identity,
            "protocol_contract_decision_sha256": triangle_contract_decision_sha256,
            "composed_ptx_sha256": triangle_composed_ptx_sha256,
            "warmup_count": args.warmups,
            "repetition_count": args.repetitions,
            "lifecycle": triangle_lifecycle,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(json.dumps(
        result, indent=2, sort_keys=True).encode("utf-8") + b"\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
