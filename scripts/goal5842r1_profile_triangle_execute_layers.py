#!/usr/bin/env python3
"""Non-claim diagnostic that separates V4 triangle execute-layer costs."""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time
from unittest.mock import patch

from experiments.goal5842_causal_admission.contracts import TRIANGLE_TASK
from experiments.goal5842_causal_admission.tasks import (
    build_task,
    build_triangle_auxiliary_program,
)
from rtdsl import v4_triangle_reduction_prepared_runtime as triangle_runtime
from rtdsl.physical_execution_provenance import OptixTraversalAuditSession
from rtdsl.v4 import FormalNumbaLeafCachePolicy, V4Target, V4Toolchain


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _timed(callable_):
    started = time.perf_counter_ns()
    result = callable_()
    return result, time.perf_counter_ns() - started


def _summary(samples_ns: list[int]) -> dict[str, object]:
    samples_ms = [value / 1_000_000.0 for value in samples_ns]
    return {
        "sample_count": len(samples_ms),
        "samples_ms": samples_ms,
        "minimum_ms": min(samples_ms),
        "median_ms": statistics.median(samples_ms),
        "maximum_ms": max(samples_ms),
    }


def _samples(callable_, *, expected: int, warmups: int, repetitions: int):
    for _ in range(warmups):
        if int(callable_()) != expected:
            raise RuntimeError("layer warmup scalar mismatch")
    samples: list[int] = []
    for _ in range(repetitions):
        observed, elapsed = _timed(callable_)
        if int(observed) != expected:
            raise RuntimeError("layer sample scalar mismatch")
        samples.append(elapsed)
    return _summary(samples)


class _BypassAuditSession:
    """Diagnostic-only replacement used to isolate audit-session cost."""

    @classmethod
    def open(cls, **_kwargs):
        return cls()

    def finish(self, **_kwargs):
        return {"physical_executor_classification": "optix_traversal_observed"}

    def abort(self) -> None:
        return None


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--warmups", type=int, default=8)
    parser.add_argument("--repetitions", type=int, default=32)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    if args.cache_root.exists() or args.cache_root.is_symlink():
        raise FileExistsError(args.cache_root)
    if args.warmups < 1 or args.repetitions < 2:
        raise ValueError("positive warmups and at least two repetitions required")
    source_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    source_status = subprocess.run(
        ["git", "status", "--porcelain"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if source_status:
        raise RuntimeError("layer diagnostic requires a clean exact source checkout")

    native = args.native.resolve(strict=True)
    capability = tuple(int(value) for value in args.compute_capability.split("."))
    target = V4Target.from_native(
        native,
        optix_sdk=args.optix_sdk,
        compute_capability=capability,
    )
    toolchain = V4Toolchain.current(
        compute_capability=capability,
        optix_include=args.optix_include,
        cuda_include=args.cuda_include,
        formal_leaf_cache=FormalNumbaLeafCachePolicy(args.cache_root),
    )
    task = build_task(TRIANGLE_TASK)
    expected = int(task.expected_output["weighted_sum"])

    program = build_triangle_auxiliary_program()
    materialized, materialize_ns = _timed(
        lambda: program.materialize(target=target, toolchain=toolchain)
    )
    prepared, prepare_ns = _timed(
        lambda: materialized.prepare(task.static_input)
    )
    try:
        first = prepared.execute(task.batch)
        if first.output != expected:
            raise RuntimeError("initial public scalar mismatch")
        owner = prepared._owner
        metadata = task.batch.metadata_dict()

        def public_call() -> int:
            return int(prepared.execute(task.batch).output)

        def provider_call() -> int:
            return int(
                owner.execute(
                    task.batch.queries,
                    query_metadata=metadata,
                    include_diagnostics=False,
                ).reduced_output
            )

        public = _samples(
            public_call,
            expected=expected,
            warmups=args.warmups,
            repetitions=args.repetitions,
        )
        provider = _samples(
            provider_call,
            expected=expected,
            warmups=args.warmups,
            repetitions=args.repetitions,
        )
        with patch.object(
            triangle_runtime,
            "OptixTraversalAuditSession",
            _BypassAuditSession,
        ):
            provider_without_audit = _samples(
                provider_call,
                expected=expected,
                warmups=args.warmups,
                repetitions=args.repetitions,
            )

        (
            origins_f32,
            directions_f32,
            tmax_f32,
            _normalized,
            multiplier_native,
            query_digest_native,
        ) = owner._cached_query_inputs
        origin_native = origins_f32.ctypes.data_as(
            ctypes.POINTER(ctypes.c_float)
        )
        direction_native = directions_f32.ctypes.data_as(
            ctypes.POINTER(ctypes.c_float)
        )
        tmax_native = tmax_f32.ctypes.data_as(ctypes.POINTER(ctypes.c_float))
        scalar = ctypes.c_uint64()
        compact_status = ctypes.c_uint32()
        error = ctypes.create_string_buffer(16384)

        def native_v7_call() -> int:
            receipt = triangle_runtime._FastPathReceipt()
            triangle_runtime._raise(
                int(
                    owner._execute_scalar(
                        owner._token,
                        origin_native,
                        direction_native,
                        tmax_native,
                        len(task.batch.queries),
                        1,
                        1,
                        1,
                        query_digest_native,
                        32,
                        multiplier_native,
                        ctypes.byref(scalar),
                        ctypes.byref(compact_status),
                        ctypes.byref(receipt),
                        error,
                        len(error),
                    )
                ),
                error,
                "Goal5842R1 direct native-v7 diagnostic",
            )
            triangle_runtime._validate_fast_receipt(
                receipt,
                query_count=len(task.batch.queries),
                compact_status=int(compact_status.value),
                prepared_input_reused=True,
                use_multipliers=True,
            )
            return int(scalar.value)

        native_v7 = _samples(
            native_v7_call,
            expected=expected,
            warmups=args.warmups,
            repetitions=args.repetitions,
        )

        def audit_begin_abort() -> int:
            audit = OptixTraversalAuditSession.open(library=owner._library)
            audit.abort()
            return expected

        audit_only = _samples(
            audit_begin_abort,
            expected=expected,
            warmups=args.warmups,
            repetitions=args.repetitions,
        )
    finally:
        prepared.close()

    result = {
        "schema": "rtdl.goal5842r1.triangle_execute_layer_diagnostic.v1",
        "status": "PASS__NONFORMAL_ENGINEERING_DIAGNOSTIC",
        "source_commit": source_commit,
        "python": sys.version.split()[0],
        "native_sha256": _sha256_file(native),
        "query_count": len(task.batch.queries),
        "expected_scalar": expected,
        "materialize_ms": materialize_ns / 1_000_000.0,
        "prepare_ms": prepare_ns / 1_000_000.0,
        "layers": {
            "public_api": public,
            "provider_owner_with_audit": provider,
            "provider_owner_without_audit": provider_without_audit,
            "native_v7_reused_input": native_v7,
            "audit_begin_abort_without_launch": audit_only,
        },
        "claim_boundary": {
            "formal_performance_evidence": False,
            "public_or_manuscript_claim_authorized": False,
            "private_runtime_internals_used": True,
            "audit_bypass_is_supported_execution": False,
        },
    }
    body = json.dumps(result, sort_keys=True, separators=(",", ":"))
    result["result_sha256"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
