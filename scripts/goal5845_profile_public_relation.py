#!/usr/bin/env python3
"""Nonformal layer profile for the optimized public bounded-relation route."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import statistics
import struct
import time
from collections.abc import Callable
from typing import Any

from experiments.goal5842_causal_admission.contracts import RELATION_TASK
from experiments.goal5842_causal_admission.tasks import build_task


def _measure(action: Callable[[], Any]) -> tuple[Any, int]:
    started = time.perf_counter_ns()
    value = action()
    return value, time.perf_counter_ns() - started


def _sample(
    action: Callable[[], object],
    validate: Callable[[object], None],
    *,
    warmups: int,
    repetitions: int,
) -> list[int]:
    for _ in range(warmups):
        validate(action())
    values: list[int] = []
    for _ in range(repetitions):
        result, elapsed = _measure(action)
        validate(result)
        values.append(elapsed)
    return values


def _summary(values: list[int]) -> dict[str, object]:
    return {
        "sample_count": len(values),
        "minimum_ns": min(values),
        "median_ns": int(statistics.median(values)),
        "maximum_ns": max(values),
    }


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _deep_owner(prepared: object) -> object:
    return prepared._handle._prepared._owner


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument("--warmups", type=int, default=8)
    parser.add_argument("--repetitions", type=int, default=64)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if min(args.warmups, args.repetitions) <= 0:
        raise ValueError("positive timing counts required")
    if args.output is not None and args.output.exists():
        raise FileExistsError(args.output)

    from rtdsl import v4_bounded_relation_prepared_runtime as relation_runtime
    from rtdsl.physical_execution_provenance import (
        NativeTraversalAuditSnapshot,
        build_validated_compact_traversal_receipt,
        validate_bound_compact_traversal_receipt,
    )
    from rtdsl.v4 import FormalNumbaLeafCachePolicy, V4Target, V4Toolchain

    task = build_task(RELATION_TASK)
    native = args.native.resolve(strict=True)
    capability = tuple(int(part) for part in args.compute_capability.split("."))
    target = V4Target.from_native(
        native,
        optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability,
    )
    toolchain = V4Toolchain.current(
        compute_capability=capability,
        optix_include=args.optix_include.resolve(strict=True),
        cuda_include=args.cuda_include.resolve(strict=True),
        formal_leaf_cache=FormalNumbaLeafCachePolicy(args.cache_root),
    )
    route, declaration_ns = _measure(task.route_factory)
    program, admission_ns = _measure(route.compile)
    materialized, materialize_ns = _measure(
        lambda: program.materialize(target=target, toolchain=toolchain)
    )
    prepared, prepare_ns = _measure(lambda: materialized.prepare(task.static_input))
    expected = task.expected_output

    def validate_public(result: object) -> None:
        if result.output != expected:
            raise RuntimeError("public bounded-relation output differs from oracle")
        validate_bound_compact_traversal_receipt(
            result.traversal_receipt,
            provider_library_sha256=materialized.identity.provider_artifact_sha256,
            route_identity="v4_callback_ir:custom_aabb_bounded_relation_v1",
            output_digest=result.output_sha256,
            expected_program_bundle="v4_custom_aabb_bounded_relation_composed",
            expected_raygen_invocation_count=(
                len(task.batch.source_boxes) + len(task.static_input.indexed_boxes)
            ),
            expected_successful_launch_count=2,
        )

    try:
        first, first_ns = _measure(lambda: prepared.execute(task.batch))
        validate_public(first)
        public_samples = _sample(
            lambda: prepared.execute(task.batch),
            validate_public,
            warmups=args.warmups,
            repetitions=args.repetitions,
        )

        bridge = prepared._handle

        def validate_bridge(result: object) -> None:
            if result.output_document != expected:
                raise RuntimeError("family bridge output differs from oracle")

        bridge_samples = _sample(
            lambda: bridge.execute(task.batch),
            validate_bridge,
            warmups=args.warmups,
            repetitions=args.repetitions,
        )

        protocol_prepared = bridge._prepared

        def validate_protocol(result: object) -> None:
            if result.output != expected:
                raise RuntimeError("protocol output differs from oracle")

        protocol_samples = _sample(
            lambda: protocol_prepared.execute(task.batch),
            validate_protocol,
            warmups=args.warmups,
            repetitions=args.repetitions,
        )

        owner = _deep_owner(prepared)

        def validate_owner(result: object) -> None:
            if result.rows != expected:
                raise RuntimeError("prepared owner output differs from oracle")

        owner_samples = _sample(
            lambda: owner.execute(
                task.batch.source_boxes,
                expected_rows=task.batch.expected_rows,
            ),
            validate_owner,
            warmups=args.warmups,
            repetitions=args.repetitions,
        )

        source_native, source_ids = owner._cached_source_native
        capacity = owner._contract.capacity
        row_storage = (ctypes.c_uint32 * (capacity * 2))()
        raw_count = ctypes.c_uint64()
        unique_count = ctypes.c_uint64()
        overflowed = ctypes.c_uint32()
        compact_status = ctypes.c_uint32()
        fast_receipt = relation_runtime._FastPathReceipt()
        audit_snapshot = NativeTraversalAuditSnapshot()
        error = ctypes.create_string_buffer(16384)
        expected_packed = b"".join(
            struct.pack("<II", int(left), int(right)) for left, right in expected
        )
        direct_sequence = 0

        def direct_native_call() -> tuple[int, int, int, int]:
            nonlocal direct_sequence
            direct_sequence += 1
            relation_runtime._raise(
                int(
                    owner._execute_fast_integrated(
                        owner._token,
                        source_native,
                        source_ids,
                        len(task.batch.source_boxes),
                        1,
                        ctypes.byref(raw_count),
                        ctypes.byref(unique_count),
                        ctypes.byref(overflowed),
                        row_storage,
                        ctypes.byref(compact_status),
                        ctypes.byref(fast_receipt),
                        0x5845000000000001,
                        direct_sequence,
                        ctypes.byref(audit_snapshot),
                        error,
                        len(error),
                    )
                ),
                error,
                "Goal5845 direct native v8",
            )
            return (
                int(raw_count.value),
                int(unique_count.value),
                int(overflowed.value),
                direct_sequence,
            )

        def validate_direct(result: object) -> None:
            raw, unique, overflow, sequence = result
            if unique != len(expected) or overflow != 0 or raw < unique:
                raise RuntimeError("direct native counts differ from oracle")
            relation_runtime._validate_fast_receipt(
                fast_receipt,
                compact_status=int(compact_status.value),
                output_row_count=unique,
                prepared_input_reused=True,
                source_count=len(task.batch.source_boxes),
                semantic_capacity=capacity,
                previous_input_generation=0,
                expected_reused_generation=owner._cached_source_generation,
            )
            if ctypes.string_at(ctypes.addressof(row_storage), unique * 8) != expected_packed:
                raise RuntimeError("direct native row bytes differ from oracle")
            receipt = build_validated_compact_traversal_receipt(
                audit_snapshot,
                provider_library_sha256=owner._native_sha,
                route_identity=owner._route_identity,
                semantic_digest=owner._semantic_digest,
                output_digest=owner._cached_output_sha,
                expected_program_bundle=owner._program_bundle,
                expected_raygen_invocation_count=(
                    len(task.batch.source_boxes) + owner.indexed_count
                ),
                execution_sequence=sequence,
                expected_successful_launch_count=2,
            )
            validate_bound_compact_traversal_receipt(
                receipt,
                provider_library_sha256=owner._native_sha,
                route_identity=owner._route_identity,
                output_digest=owner._cached_output_sha,
                expected_program_bundle=owner._program_bundle,
                expected_raygen_invocation_count=(
                    len(task.batch.source_boxes) + owner.indexed_count
                ),
                expected_successful_launch_count=2,
            )

        direct_samples = _sample(
            direct_native_call,
            validate_direct,
            warmups=args.warmups,
            repetitions=args.repetitions,
        )

        diagnostic, diagnostic_ns = _measure(
            lambda: protocol_prepared.execute(
                task.batch, include_diagnostics=True
            )
        )
        if diagnostic.output != expected or not diagnostic.details:
            raise RuntimeError("explicit diagnostic execution differs from oracle")
        fast_receipt_values = dict(owner._last_fast_operation_receipt)
    finally:
        prepared.close()

    result = {
        "schema": "rtdl.goal5845.public_relation_layer_profile.v1",
        "status": "PASS__NONFORMAL_ENGINEERING_DIAGNOSTIC",
        "native_sha256": _sha256_file(native),
        "query_count": len(task.batch.source_boxes),
        "row_count": len(expected),
        "first_public_ns": first_ns,
        "steady": {
            "full_public_family": _summary(public_samples),
            "family_bridge": _summary(bridge_samples),
            "protocol_lifecycle": _summary(protocol_samples),
            "prepared_owner": _summary(owner_samples),
            "direct_native_v8": _summary(direct_samples),
        },
        "explicit_diagnostic_execution_ns": diagnostic_ns,
        "fast_operation_receipt": fast_receipt_values,
        "setup_ns": {
            "route_declaration": declaration_ns,
            "generic_admission": admission_ns,
            "materialize": materialize_ns,
            "prepare": prepare_ns,
        },
        "claim_boundary": {
            "formal_performance_claim_authorized": False,
            "external_review_complete": False,
        },
    }
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
