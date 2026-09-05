"""Isolated RTDL or pinned-PyOptiX bounded-relation steady worker."""

from __future__ import annotations

import argparse
import ctypes
import gc
import hashlib
import importlib.metadata
import json
from pathlib import Path
import statistics
import struct
import subprocess
import sys
import time
from collections.abc import Callable
from typing import Any

from experiments.goal5842_causal_admission.contracts import RELATION_TASK, digest
from experiments.goal5842_causal_admission.tasks import build_task
from experiments.goal5844_compact_execution.provenance import (
    validate_pyoptix_build_receipt,
    write_json_create,
)


RTDL_ARM = "RTDL_PUBLIC_RELATION_V8_COMPACT_STAMP"
PYOPTIX_ARM = "PINNED_PYOPTIX_COMPATIBLE_API"
ARMS = (RTDL_ARM, PYOPTIX_ARM)
PYOPTIX_COMMIT = "3144f224c0fd18733925faf3d8fb82c7376b8dcf"
PYOPTIX_TREE = "0bf0ec24efb4a43f129aee25dd265aa8149374e3"


def _sha256_file(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


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
) -> tuple[list[int], object]:
    latest: object | None = None
    for _ in range(warmups):
        latest = action()
        validate(latest)
    values: list[int] = []
    for _ in range(repetitions):
        latest, elapsed = _measure(action)
        validate(latest)
        values.append(elapsed)
    if latest is None:
        raise RuntimeError("Goal5845 timing loop produced no result")
    return values, latest


def _summary(values: list[int]) -> dict[str, object]:
    if not values:
        raise ValueError("nonempty timing samples required")
    return {
        "sample_count": len(values),
        "samples_ns": values,
        "minimum_ns": min(values),
        "median_ns": int(statistics.median(values)),
        "maximum_ns": max(values),
    }


def _hardware() -> dict[str, object]:
    fields = "name,uuid,driver_version,memory.total,compute_cap"
    completed = subprocess.run(
        [
            "nvidia-smi",
            "--id=0",
            f"--query-gpu={fields}",
            "--format=csv,noheader,nounits",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    rows = [row.strip() for row in completed.stdout.splitlines() if row.strip()]
    if len(rows) != 1:
        raise RuntimeError("Goal5845 worker requires exactly one visible GPU")
    parts = [part.strip() for part in rows[0].split(",")]
    if len(parts) != 5:
        raise RuntimeError("Goal5845 observed an unexpected GPU identity row")
    return {
        "gpu_name": parts[0],
        "gpu_uuid": parts[1],
        "driver_version": parts[2],
        "memory_mib": int(parts[3]),
        "compute_capability": parts[4],
    }


def _git_identity(path: Path) -> dict[str, object]:
    root = path.resolve(strict=True)
    values = {}
    for label, arguments in (
        ("commit", ("rev-parse", "HEAD")),
        ("tree", ("rev-parse", "HEAD^{tree}")),
        ("status", ("status", "--porcelain=v1", "--untracked-files=all")),
    ):
        values[label] = subprocess.run(
            ["git", "-C", str(root), *arguments],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    return {"path": str(root), **values, "clean": values["status"] == ""}


def _run_rtdl(args: argparse.Namespace, task: object) -> dict[str, object]:
    from rtdsl import v4_bounded_relation_prepared_runtime as relation_runtime
    from rtdsl.physical_execution_provenance import (
        NativeTraversalAuditSnapshot,
        build_validated_compact_traversal_receipt,
        validate_bound_compact_traversal_receipt,
        validate_traversal_receipt,
    )
    from rtdsl.v4 import FormalNumbaLeafCachePolicy, V4Target, V4Toolchain

    native = args.native.resolve(strict=True)
    target = V4Target.from_native(
        native,
        optix_sdk=args.optix_sdk,
        compute_capability=args.compute_capability,
    )
    capability = tuple(int(part) for part in args.compute_capability.split("."))
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
    expected_sha = digest(expected)
    raygen_count = len(task.batch.source_boxes) + len(task.static_input.indexed_boxes)

    def validate_public(result: object) -> None:
        if (
            type(result.output) is not relation_runtime.ValidatedBoundedRelationRows
            or result.output != expected
            or result.output_sha256 != expected_sha
        ):
            raise RuntimeError("Goal5845 RTDL public output differs from oracle")
        relation_runtime.validate_bound_relation_rows(
            result.output, output_sha256=expected_sha
        )
        validate_bound_compact_traversal_receipt(
            result.traversal_receipt,
            provider_library_sha256=materialized.identity.provider_artifact_sha256,
            route_identity="v4_callback_ir:custom_aabb_bounded_relation_v1",
            output_digest=expected_sha,
            expected_program_bundle="v4_custom_aabb_bounded_relation_composed",
            expected_raygen_invocation_count=raygen_count,
            expected_successful_launch_count=2,
        )

    try:
        first, first_ns = _measure(lambda: prepared.execute(task.batch))
        validate_public(first)
        retained_output = first.output
        public_samples, latest_public = _sample(
            lambda: prepared.execute(task.batch),
            validate_public,
            warmups=args.warmups,
            repetitions=args.repetitions,
        )
        if latest_public.output is not retained_output:
            raise RuntimeError("Goal5845 RTDL did not reuse immutable public rows")

        bridge = prepared._handle

        def validate_bridge(result: object) -> None:
            if result.output_document is not retained_output:
                raise RuntimeError("Goal5845 family bridge copied relation rows")

        bridge_samples, _latest_bridge = _sample(
            lambda: bridge.execute(task.batch),
            validate_bridge,
            warmups=args.layer_warmups,
            repetitions=args.layer_repetitions,
        )

        protocol = bridge._prepared

        def validate_protocol(result: object) -> None:
            if result.output is not retained_output or result.output_sha256 != expected_sha:
                raise RuntimeError("Goal5845 protocol output differs")

        protocol_samples, _latest_protocol = _sample(
            lambda: protocol.execute(task.batch),
            validate_protocol,
            warmups=args.layer_warmups,
            repetitions=args.layer_repetitions,
        )

        owner = protocol._owner

        def validate_owner(result: object) -> None:
            if result.rows is not retained_output or result.output_sha256 != expected_sha:
                raise RuntimeError("Goal5845 owner output differs")

        owner_samples, _latest_owner = _sample(
            lambda: owner.execute(
                task.batch.source_boxes,
                expected_rows=task.batch.expected_rows,
            ),
            validate_owner,
            warmups=args.layer_warmups,
            repetitions=args.layer_repetitions,
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

        def direct_call() -> tuple[int, int, int, int]:
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
            if raw < unique or unique != len(expected) or overflow != 0:
                raise RuntimeError("Goal5845 direct native counts differ")
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
                raise RuntimeError("Goal5845 direct native bytes differ")
            receipt = build_validated_compact_traversal_receipt(
                audit_snapshot,
                provider_library_sha256=owner._native_sha,
                route_identity=owner._route_identity,
                semantic_digest=owner._semantic_digest,
                output_digest=expected_sha,
                expected_program_bundle=owner._program_bundle,
                expected_raygen_invocation_count=raygen_count,
                execution_sequence=sequence,
                expected_successful_launch_count=2,
            )
            validate_bound_compact_traversal_receipt(
                receipt,
                provider_library_sha256=owner._native_sha,
                route_identity=owner._route_identity,
                output_digest=expected_sha,
                expected_program_bundle=owner._program_bundle,
                expected_raygen_invocation_count=raygen_count,
                expected_successful_launch_count=2,
            )

        direct_samples, _latest_direct = _sample(
            direct_call,
            validate_direct,
            warmups=args.layer_warmups,
            repetitions=args.layer_repetitions,
        )
        compact_receipt = dict(latest_public.traversal_receipt)
        validate_traversal_receipt(
            compact_receipt,
            provider_library_sha256=owner._native_sha,
            route_identity=owner._route_identity,
            output_digest=expected_sha,
            expected_program_bundles=(owner._program_bundle,),
            expected_successful_launch_count=2,
            expected_raygen_invocation_count=raygen_count,
        )
        fast_operation = dict(owner._last_fast_operation_receipt)
        diagnostic, diagnostic_ns = _measure(
            lambda: protocol.execute(task.batch, include_diagnostics=True)
        )
        if diagnostic.output != expected or not diagnostic.details:
            raise RuntimeError("Goal5845 RTDL diagnostic output differs")
    finally:
        close_started = time.perf_counter_ns()
        prepared.close()
        close_ns = time.perf_counter_ns() - close_started

    return {
        "first_execution_ns": first_ns,
        "steady_public": _summary(public_samples),
        "attribution": {
            "family_bridge": _summary(bridge_samples),
            "protocol_lifecycle": _summary(protocol_samples),
            "prepared_owner": _summary(owner_samples),
            "direct_native_v8": _summary(direct_samples),
            "explicit_full_diagnostic_ns": diagnostic_ns,
        },
        "setup_ns": {
            "route_declaration": declaration_ns,
            "generic_admission": admission_ns,
            "materialize": materialize_ns,
            "prepare": prepare_ns,
            "close": close_ns,
        },
        "identity": {
            "native_library_sha256": _sha256_file(native),
            "generic_executable_identity": materialized.identity.to_dict(),
        },
        "evidence": {
            "public_output_sha256": expected_sha,
            "public_row_count": len(expected),
            "latest_compact_receipt": compact_receipt,
            "latest_fast_operation_receipt": fast_operation,
            "immutable_output_reused": True,
            "two_actual_optix_launches": True,
        },
    }


def _run_pyoptix(args: argparse.Namespace, task: object) -> dict[str, object]:
    from experiments.goal5796_matched import pyoptix_baseline as baseline
    from experiments.goal5798_premeasurement.pyoptix_worker import (
        PyOptixRelationPrepared,
    )

    if baseline.PYOPTIX_COMMIT != PYOPTIX_COMMIT:
        raise RuntimeError("Goal5845 PyOptiX commit constant differs")
    source = _git_identity(args.pyoptix_source)
    if (
        source["commit"] != PYOPTIX_COMMIT
        or source["tree"] != PYOPTIX_TREE
        or source["clean"] is not True
    ):
        raise RuntimeError("Goal5845 PyOptiX source identity differs")
    expected_api = tuple(int(part) for part in args.optix_sdk.split("."))
    if tuple(int(part) for part in baseline.optix.version()) != expected_api:
        raise RuntimeError("Goal5845 PyOptiX API differs")
    receipt = validate_pyoptix_build_receipt(
        args.pyoptix_build_receipt.resolve(strict=True)
    )
    ptx, compile_ns = _measure(
        lambda: baseline.compile_ptx(
            args.device_source.resolve(strict=True),
            args.optix_include.resolve(strict=True),
            args.cuda_include.resolve(strict=True),
        )
    )

    def create_pipeline():
        context, logger = baseline.make_context()
        pipeline, groups, logs = baseline.build_pipeline(
            context, ptx, task="relation"
        )
        sbt, keepalive = baseline.make_sbt(groups)
        return context, logger, pipeline, groups, logs, sbt, keepalive

    state, pipeline_ns = _measure(create_pipeline)
    context, _logger, pipeline, _groups, _logs, sbt, _keepalive = state
    prepared, prepare_ns = _measure(
        lambda: PyOptixRelationPrepared(
            baseline, context, pipeline, sbt, task.provider_fixture
        )
    )
    expected = task.expected_output
    expected_sha = digest(expected)

    def execute() -> dict[str, Any]:
        return prepared.execute(validate_expected=False)

    def validate(result: object) -> None:
        if not isinstance(result, dict):
            raise TypeError("Goal5845 PyOptiX output is not a mapping")
        rows = tuple(tuple(int(item) for item in row) for row in result["output"])
        if (
            rows != expected
            or digest(rows) != expected_sha
            or int(result["device_status"]) != 0
            or int(result["device_overflow"]) != 0
        ):
            raise RuntimeError("Goal5845 PyOptiX output differs from oracle")

    first, first_ns = _measure(execute)
    validate(first)
    samples, latest = _sample(
        execute,
        validate,
        warmups=args.warmups,
        repetitions=args.repetitions,
    )
    close_started = time.perf_counter_ns()
    prepared = None
    state = None
    sbt = None
    pipeline = None
    context = None
    gc.collect()
    baseline.cp.get_default_memory_pool().free_all_blocks()
    close_ns = time.perf_counter_ns() - close_started

    extension = sys.modules.get("optix._optix")
    extension_path = Path(getattr(extension, "__file__", "")).resolve(strict=True)
    extension_sha = _sha256_file(extension_path)
    bound_extension = receipt["installed"]["loaded_extension"]
    if (
        extension_path.stat().st_size != bound_extension["bytes"]
        or extension_sha != bound_extension["sha256"]
        or extension_sha != receipt["wheel"]["extension_sha256"]
    ):
        raise RuntimeError("Goal5845 loaded PyOptiX extension differs")
    return {
        "first_execution_ns": first_ns,
        "steady_public": _summary(samples),
        "attribution": None,
        "setup_ns": {
            "device_compile": compile_ns,
            "pipeline": pipeline_ns,
            "prepare": prepare_ns,
            "close": close_ns,
        },
        "identity": {
            "device_source_sha256": _sha256_file(args.device_source),
            "ptx_sha256": hashlib.sha256(ptx).hexdigest(),
            "pyoptix_repository": source,
            "pyoptix_distribution": args.pyoptix_distribution,
            "pyoptix_distribution_version": importlib.metadata.version(
                args.pyoptix_distribution
            ),
            "optix_api_version": ".".join(str(part) for part in baseline.optix.version()),
            "cupy_version": baseline.cp.__version__,
            "loaded_extension": {
                "path": str(extension_path),
                "bytes": extension_path.stat().st_size,
                "sha256": extension_sha,
            },
            "pyoptix_build_receipt_sha256": receipt["receipt_sha256"],
        },
        "evidence": {
            "public_output_sha256": expected_sha,
            "public_row_count": len(expected),
            "raw_event_count": int(latest["raw_event_count"]),
            "duplicate_count": int(latest["duplicate_count"]),
            "device_status": int(latest["device_status"]),
            "device_overflow": int(latest["device_overflow"]),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=ARMS, required=True)
    parser.add_argument("--block", type=int, required=True)
    parser.add_argument("--expected-source-commit", required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--device-source", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument("--pyoptix-distribution", default="pyoptix")
    parser.add_argument("--pyoptix-source", type=Path, required=True)
    parser.add_argument("--pyoptix-build-receipt", type=Path, required=True)
    parser.add_argument("--warmups", type=int, default=16)
    parser.add_argument("--repetitions", type=int, default=128)
    parser.add_argument("--layer-warmups", type=int, default=8)
    parser.add_argument("--layer-repetitions", type=int, default=64)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or args.output.is_symlink():
        raise FileExistsError(args.output)
    if args.block < 0 or min(
        args.warmups,
        args.repetitions,
        args.layer_warmups,
        args.layer_repetitions,
    ) <= 0:
        raise ValueError("Goal5845 timing arguments are invalid")
    root = Path(__file__).resolve().parents[2]
    source = _git_identity(root)
    if source["clean"] is not True or source["commit"] != args.expected_source_commit:
        raise RuntimeError("Goal5845 worker requires the exact clean source commit")
    hardware_before = _hardware()
    if hardware_before["compute_capability"] != args.compute_capability:
        raise RuntimeError("Goal5845 compute capability differs from visible GPU")
    task = build_task(RELATION_TASK)
    measurements = (
        _run_rtdl(args, task)
        if args.arm == RTDL_ARM
        else _run_pyoptix(args, task)
    )
    hardware_after = _hardware()
    if hardware_after != hardware_before:
        raise RuntimeError("Goal5845 GPU identity changed during worker")
    result: dict[str, object] = {
        "schema": "rtdl.goal5845.relation_compact_execution.worker.v1",
        "status": "PASS__INTERNAL_ENGINEERING_WORKER",
        "source_commit": source["commit"],
        "source_tree": source["tree"],
        "arm": args.arm,
        "block": args.block,
        "python": sys.version.split()[0],
        "hardware": hardware_before,
        "task": RELATION_TASK,
        "query_count": len(task.batch.source_boxes),
        "row_count": len(task.expected_output),
        "output_sha256": digest(task.expected_output),
        "warmups": args.warmups,
        "repetitions": args.repetitions,
        "measurements": measurements,
        "claim_boundary": {
            "engineering_evidence_only": True,
            "public_or_manuscript_claim_authorized": False,
            "external_review_complete": False,
        },
    }
    result["result_sha256"] = digest(result)
    write_json_create(args.output, result)
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
