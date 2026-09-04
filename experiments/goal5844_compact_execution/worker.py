"""Isolated RTDL or pinned-PyOptiX triangle steady-execution worker."""

from __future__ import annotations

import argparse
import ctypes
import gc
import hashlib
import importlib.metadata
import json
from pathlib import Path
import statistics
import subprocess
import sys
import time
from typing import Any, Callable

from experiments.goal5842_causal_admission.contracts import TRIANGLE_TASK, digest
from experiments.goal5842_causal_admission.tasks import build_task


ROOT = Path(__file__).resolve().parents[2]
RTDL_ARM = "RTDL_PUBLIC_V8_COMPACT_STAMP"
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
    fields = (
        "name,uuid,driver_version,memory.total,compute_cap"
    )
    completed = subprocess.run(
        [
            "nvidia-smi",
            f"--query-gpu={fields}",
            "--format=csv,noheader,nounits",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    rows = [row.strip() for row in completed.stdout.splitlines() if row.strip()]
    if len(rows) != 1:
        raise RuntimeError("Goal5844 worker requires exactly one visible NVIDIA GPU")
    parts = [part.strip() for part in rows[0].split(",")]
    if len(parts) != 5:
        raise RuntimeError("unexpected nvidia-smi identity row")
    return {
        "gpu_name": parts[0],
        "gpu_uuid": parts[1],
        "driver_version": parts[2],
        "memory_mib": int(parts[3]),
        "compute_capability": parts[4],
    }


def _deep_owner(prepared: object) -> object:
    bridge = getattr(prepared, "_handle")
    protocol_prepared = getattr(bridge, "_prepared")
    return getattr(protocol_prepared, "_owner")


def _run_rtdl(args: argparse.Namespace, task: object) -> dict[str, object]:
    from rtdsl.physical_execution_provenance import (
        NativeTraversalAuditSnapshot,
        validate_traversal_receipt,
    )
    from rtdsl.v4 import FormalNumbaLeafCachePolicy, V4Target, V4Toolchain
    from rtdsl import v4_triangle_reduction_prepared_runtime as triangle_runtime

    native = args.native.resolve(strict=True)
    capability = tuple(int(part) for part in args.compute_capability.split("."))
    target = V4Target.from_native(
        native,
        optix_sdk=args.optix_sdk,
        compute_capability=capability,
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
    expected = int(task.expected_output["weighted_sum"])
    expected_digest = digest(expected)

    latest_public: object | None = None

    def public_call() -> object:
        nonlocal latest_public
        latest_public = prepared.execute(task.batch)
        return latest_public

    def validate_public(result: object) -> None:
        if type(result.output) is not int or result.output != expected:
            raise RuntimeError("Goal5844 RTDL public scalar differs from oracle")
        if result.output_sha256 != expected_digest:
            raise RuntimeError("Goal5844 RTDL public output digest differs")
        validate_traversal_receipt(
            result.traversal_receipt,
            provider_library_sha256=materialized.identity.provider_artifact_sha256,
            route_identity="v4_builtin_triangle_callback_ir:checked_reduction_v1",
            output_digest=result.output_sha256,
            expected_program_bundles=(
                "v4_builtin_triangle_checked_reduction_composed",
            ),
            expected_successful_launch_count=1,
            expected_raygen_invocation_count=len(task.batch.queries),
        )

    try:
        first, first_ns = _measure(public_call)
        validate_public(first)
        public_samples = _sample(
            public_call,
            validate_public,
            warmups=args.warmups,
            repetitions=args.repetitions,
        )

        owner = _deep_owner(prepared)
        metadata = task.batch.metadata_dict()
        latest_provider: object | None = None

        def provider_call() -> object:
            nonlocal latest_provider
            latest_provider = owner.execute(
                task.batch.queries,
                query_metadata=metadata,
                include_diagnostics=False,
            )
            return latest_provider

        def validate_provider(result: object) -> None:
            if result.reduced_output != expected:
                raise RuntimeError("Goal5844 provider scalar differs from oracle")
            validate_traversal_receipt(
                result.traversal_receipt,
                provider_library_sha256=owner._native_sha,
                route_identity=owner._route_identity,
                output_digest=result.output_sha256,
                expected_program_bundles=(owner._program_bundle,),
                expected_successful_launch_count=1,
                expected_raygen_invocation_count=len(task.batch.queries),
            )

        provider_samples = _sample(
            provider_call,
            validate_provider,
            warmups=args.layer_warmups,
            repetitions=args.layer_repetitions,
        )
        if latest_public is None or latest_provider is None:
            raise RuntimeError("Goal5844 RTDL worker lacks retained execution evidence")

        # Retain the provider-owned observation before entering lower-layer
        # attribution. The direct-native probe uses separate scratch state.
        forensic_samples: list[int] = []
        forensic: object | None = None
        for _ in range(args.layer_repetitions):
            forensic, elapsed = _measure(owner.last_forensic_traversal_receipt)
            if forensic["output_digest"] != expected_digest:
                raise RuntimeError("Goal5844 forensic expansion output differs")
            forensic_samples.append(elapsed)
        if forensic is None:
            raise RuntimeError("Goal5844 forensic expansion evidence missing")

        (
            _origins,
            _directions,
            _tmax,
            _normalized,
            multiplier_native,
            query_digest_native,
        ) = owner._cached_query_inputs
        origin_native, direction_native, tmax_native = owner._cached_query_pointers
        scalar = ctypes.c_uint64()
        compact_status = ctypes.c_uint32()
        fast_receipt = triangle_runtime._FastPathReceipt()
        audit_snapshot = NativeTraversalAuditSnapshot()
        error = ctypes.create_string_buffer(16384)
        direct_sequence = 0

        def native_call() -> tuple[int, int, int]:
            nonlocal direct_sequence
            direct_sequence += 1
            if direct_sequence >= 1 << 64:
                raise RuntimeError("Goal5844 direct attribution sequence exhausted")
            triangle_runtime._raise(
                int(
                    owner._execute_scalar_integrated(
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
                        ctypes.byref(fast_receipt),
                        0x5844000000000001,
                        direct_sequence,
                        ctypes.byref(audit_snapshot),
                        error,
                        len(error),
                    )
                ),
                error,
                "Goal5844 native-v8 attribution",
            )
            return int(scalar.value), int(compact_status.value), direct_sequence

        def validate_native(result: object) -> None:
            value, status, sequence = result
            if value != expected or status != 0:
                raise RuntimeError("Goal5844 native-v8 attribution output differs")
            triangle_runtime._validate_fast_receipt(
                fast_receipt,
                query_count=len(task.batch.queries),
                compact_status=status,
                prepared_input_reused=True,
                use_multipliers=True,
                expected_input_generation=owner._cached_query_generation,
            )
            if (
                int(audit_snapshot.nonce_hi) != 0x5844000000000001
                or int(audit_snapshot.nonce_lo) != sequence
                or int(audit_snapshot.successful_launch_count) != 1
            ):
                raise RuntimeError("Goal5844 native-v8 attribution audit differs")

        native_samples = _sample(
            native_call,
            validate_native,
            warmups=args.layer_warmups,
            repetitions=args.layer_repetitions,
        )
        boundary = owner.lifecycle_receipt["last_execution"]
        if (
            boundary["execution_path"]
            != "device_resident_checked_u64_scalar_v8_integrated_audit"
        ):
            raise RuntimeError("Goal5844 RTDL worker did not use native v8")
    finally:
        close_started = time.perf_counter_ns()
        prepared.close()
        close_ns = time.perf_counter_ns() - close_started

    return {
        "first_execution_ns": first_ns,
        "steady_public": _summary(public_samples),
        "attribution": {
            "provider_owner_v8_compact": _summary(provider_samples),
            "direct_native_abi_v8_integrated_audit": _summary(native_samples),
            "explicit_full_forensic_expansion": _summary(forensic_samples),
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
            "latest_public_compact_receipt": dict(
                latest_public.traversal_receipt
            ),
            "latest_provider_compact_receipt": dict(
                latest_provider.traversal_receipt
            ),
            "latest_full_forensic_receipt": dict(forensic),
            "execution_boundary": boundary,
        },
    }


def _run_pyoptix(args: argparse.Namespace, task: object) -> dict[str, object]:
    from experiments.goal5796_matched import pyoptix_baseline as baseline
    from experiments.goal5798_premeasurement.pyoptix_worker import (
        PyOptixTrianglePrepared,
    )

    if baseline.PYOPTIX_COMMIT != PYOPTIX_COMMIT:
        raise RuntimeError("Goal5844 pinned PyOptiX repository identity drift")
    source_identity = _git_identity(args.pyoptix_source)
    if (
        source_identity["commit"] != PYOPTIX_COMMIT
        or source_identity["tree"] != PYOPTIX_TREE
        or source_identity["clean"] is not True
    ):
        raise RuntimeError("Goal5844 PyOptiX source checkout identity differs")
    expected_api = tuple(int(part) for part in args.optix_sdk.split("."))
    if tuple(int(part) for part in baseline.optix.version()) != expected_api:
        raise RuntimeError("Goal5844 PyOptiX API differs from requested OptiX SDK")
    ptx, compile_ns = _measure(
        lambda: baseline.compile_ptx(
            args.device_source.resolve(strict=True),
            args.optix_include.resolve(strict=True),
            args.cuda_include.resolve(strict=True),
        )
    )

    def make_pipeline() -> tuple[object, ...]:
        context, logger = baseline.make_context()
        pipeline, groups, logs = baseline.build_pipeline(
            context, ptx, task="triangle"
        )
        sbt, keepalive = baseline.make_sbt(groups)
        return context, logger, pipeline, groups, logs, sbt, keepalive

    state, pipeline_ns = _measure(make_pipeline)
    context, _logger, pipeline, _groups, _logs, sbt, _keepalive = state
    prepared, prepare_ns = _measure(
        lambda: PyOptixTrianglePrepared(
            baseline, context, pipeline, sbt, task.provider_fixture
        )
    )
    expected = int(task.expected_output["weighted_sum"])

    latest_output: object | None = None

    def execute() -> object:
        nonlocal latest_output
        latest_output = prepared.execute(
            public_output_only=True, validate_expected=False
        )
        return latest_output

    def validate(result: object) -> None:
        if not isinstance(result, dict):
            raise RuntimeError("Goal5844 PyOptiX output is not a mapping")
        if int(result["device_status"]) != 0 or int(result["weighted_sum"]) != expected:
            raise RuntimeError("Goal5844 PyOptiX scalar differs from oracle")

    first, first_ns = _measure(execute)
    validate(first)
    samples = _sample(
        execute,
        validate,
        warmups=args.warmups,
        repetitions=args.repetitions,
    )
    if latest_output is None:
        raise RuntimeError("Goal5844 PyOptiX worker lacks retained output evidence")
    close_started = time.perf_counter_ns()
    prepared = None
    state = None
    sbt = None
    pipeline = None
    context = None
    gc.collect()
    baseline.cp.get_default_memory_pool().free_all_blocks()
    close_ns = time.perf_counter_ns() - close_started
    distribution_name = args.pyoptix_distribution
    extension = sys.modules.get("optix._optix")
    extension_path = getattr(extension, "__file__", None)
    if not extension_path:
        raise RuntimeError("Goal5844 loaded PyOptiX extension identity is absent")
    extension_path = Path(extension_path).resolve(strict=True)
    return {
        "first_execution_ns": first_ns,
        "steady_public": _summary(samples),
        "attribution": None,
        "setup_ns": {
            "device_compile": compile_ns,
            "module_pipeline_sbt": pipeline_ns,
            "prepare": prepare_ns,
            "close": close_ns,
        },
        "identity": {
            "device_source_sha256": _sha256_file(
                args.device_source.resolve(strict=True)
            ),
            "ptx_sha256": hashlib.sha256(ptx).hexdigest(),
            "pyoptix_repository_commit": baseline.PYOPTIX_COMMIT,
            "pyoptix_source": source_identity,
            "pyoptix_distribution": distribution_name,
            "pyoptix_distribution_version": importlib.metadata.version(
                distribution_name
            ),
            "optix_api_version": ".".join(
                str(part) for part in baseline.optix.version()
            ),
            "cupy_version": baseline.cp.__version__,
            "loaded_extension": {
                "path": str(extension_path),
                "bytes": extension_path.stat().st_size,
                "sha256": _sha256_file(extension_path),
            },
        },
        "evidence": {"latest_public_output": latest_output},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=ARMS, required=True)
    parser.add_argument("--block", type=int, required=True)
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--device-source", type=Path, required=True)
    parser.add_argument("--optix-include", type=Path, required=True)
    parser.add_argument("--cuda-include", type=Path, required=True)
    parser.add_argument("--optix-sdk", required=True)
    parser.add_argument("--compute-capability", required=True)
    parser.add_argument("--cache-root", type=Path, required=True)
    parser.add_argument("--pyoptix-distribution", default="pyoptix")
    parser.add_argument("--pyoptix-source", type=Path, required=True)
    parser.add_argument("--warmups", type=int, default=16)
    parser.add_argument("--repetitions", type=int, default=128)
    parser.add_argument("--layer-warmups", type=int, default=8)
    parser.add_argument("--layer-repetitions", type=int, default=64)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    if args.block < 0:
        raise ValueError("nonnegative block required")
    if min(
        args.warmups,
        args.repetitions,
        args.layer_warmups,
        args.layer_repetitions,
    ) <= 0:
        raise ValueError("positive timing counts required")
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    if status:
        raise RuntimeError("Goal5844 GPU worker requires a clean source checkout")
    source_commit = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    hardware_before = _hardware()
    if hardware_before["compute_capability"] != args.compute_capability:
        raise RuntimeError(
            "Goal5844 requested compute capability differs from visible GPU"
        )
    task = build_task(TRIANGLE_TASK)
    if args.arm == RTDL_ARM:
        measurements = _run_rtdl(args, task)
    else:
        measurements = _run_pyoptix(args, task)
    hardware_after = _hardware()
    if hardware_after != hardware_before:
        raise RuntimeError("Goal5844 GPU identity changed during worker")
    result: dict[str, object] = {
        "schema": "rtdl.goal5844.compact_execution.worker.v1",
        "status": "PASS__INTERNAL_ENGINEERING_WORKER",
        "source_commit": source_commit,
        "arm": args.arm,
        "block": args.block,
        "python": sys.version.split()[0],
        "hardware": hardware_before,
        "task": TRIANGLE_TASK,
        "query_count": len(task.batch.queries),
        "expected_scalar": int(task.expected_output["weighted_sum"]),
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
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
